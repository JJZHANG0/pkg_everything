from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from .models import DeliveryOrder, Robot, Message, RobotCommand
from .serializers import DeliveryOrderSerializer, RobotSerializer, UserSerializer, MessageSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .utils import generate_signed_payload, generate_qr_code
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from pyzbar.pyzbar import decode
from PIL import Image
import json, hashlib, base64
from django.conf import settings
from django.utils import timezone
from .models import SystemLog
from django.db.models import Count, Q





User = get_user_model()


# ✅ 管理员权限控制类
class IsAdminUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


# ✅ 新增：分发人员权限控制类
class IsDispatcher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_dispatcher


# ✅ 用户视图（含 /me）
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def set_dispatcher(self, request, pk=None):
        """
        设置/取消配送员身份（超级管理员专用）
        POST /api/users/<id>/set_dispatcher/
        {
          "is_dispatcher": true
        }
        """
        user = self.get_object()
        is_dispatcher = request.data.get("is_dispatcher")

        if not isinstance(is_dispatcher, bool):
            return Response({"detail": "请提供 is_dispatcher: true/false"}, status=400)

        user.is_dispatcher = is_dispatcher
        user.save()
        return Response({"id": user.id, "username": user.username, "is_dispatcher": user.is_dispatcher})


# ✅ 学生 / 老师订单接口
class DeliveryOrderViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_teacher:
            return DeliveryOrder.objects.all()
        return DeliveryOrder.objects.filter(student=user)

    def perform_create(self, serializer):
        order = serializer.save(student=self.request.user)
        
        # 构建配送信息
        delivery_info = {
            'building': order.delivery_building,
            'room': order.delivery_room or '',
            'package_type': order.package_type
        }
        
        # 生成简单二维码数据
        qr_content = generate_simple_qr_code(order.id, order.student.id)
        
        # 生成二维码图片
        qr_base64 = generate_qr_code({'payload_data': qr_content})
        
        # 保存二维码相关数据
        order.qr_code_url = qr_base64
        order.qr_payload_data = qr_content
        order.qr_signature = None  # 简化版本不需要签名
        order.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.is_teacher:
            return Response({'detail': '只有教师可以分配机器人'}, status=status.HTTP_403_FORBIDDEN)

        if instance.status != "PENDING":
            return Response({'detail': '订单已分配或正在配送中'}, status=status.HTTP_400_BAD_REQUEST)

        robot = Robot.objects.filter(is_available=True).first()
        if not robot:
            return Response({'detail': '当前无可用机器人'}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = "ASSIGNED"
        instance.teacher = request.user
        instance.save()

        robot.is_available = False
        robot.current_order = instance
        robot.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ✅ 配送人员专属订单操作接口
class DispatchOrderViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryOrderSerializer
    permission_classes = [IsDispatcher]

    def get_queryset(self):
        status_filter = self.request.query_params.get("status")
        if status_filter:
            return DeliveryOrder.objects.filter(status=status_filter)
        return DeliveryOrder.objects.all()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['PENDING', 'ASSIGNED', 'DELIVERING', 'DELIVERED']:
            return Response({"detail": "不允许设置该状态"}, status=status.HTTP_400_BAD_REQUEST)

        # 如果状态更新为"已分配"，自动分配给机器人并设置状态为LOADING
        if new_status == 'ASSIGNED':
            try:
                if not instance.robot:
                    # 如果订单还没有分配机器人，分配一个空闲机器人
                    robot = Robot.objects.filter(status='IDLE').first()
                    if robot:
                        instance.robot = robot
                    else:
                        # 如果没有空闲机器人，创建一个默认机器人
                        robot, created = Robot.objects.get_or_create(
                            id=1,
                            defaults={'name': 'Robot-001', 'status': 'IDLE'}
                        )
                        instance.robot = robot
                
                # 无论订单是否已有机器人，都将机器人状态设置为LOADING
                if instance.robot:
                    instance.robot.status = 'LOADING'
                    instance.robot.save()
                    
            except Exception as e:
                print(f"分配机器人失败: {e}")
        
        instance.status = new_status
        instance.save()
        
        # 如果状态更新为"已分配"或"配送中"，返回该订单的完整信息给机器人
        if new_status in ['ASSIGNED', 'DELIVERING']:
            order_data = {
                "order_id": instance.id,
                "status": instance.status,
                "student": {
                    "id": instance.student.id,
                    "name": instance.student.username,
                    "email": instance.student.email,
                    "first_name": instance.student.first_name,
                    "last_name": instance.student.last_name,
                },
                "package_info": {
                    "type": instance.package_type,
                    "weight": instance.weight,
                    "fragile": instance.fragile,
                    "description": instance.description,
                },
                "pickup_location": {
                    "building": instance.pickup_building,
                    "instructions": instance.pickup_instructions,
                },
                "delivery_location": {
                    "building": instance.delivery_building,
                    "room": instance.delivery_room,
                },
                "qr_code_data": {
                    "payload": instance.qr_payload_data,
                    "signature": instance.qr_signature,
                    "qr_image_url": instance.qr_code_url,
                },
                "delivery_priority": "normal",
                "estimated_time": "15分钟",
                "action": "order_loaded",  # 标识这是装货完成的订单
                "timestamp": instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
            }
            
            return Response({
                "detail": f"订单 {instance.id} 状态已更新为 {new_status}",
                "order_data": order_data,
                "robot_id": instance.robot.id if instance.robot else None,
                "robot_name": instance.robot.name if instance.robot else None
            })
        
        return Response(self.get_serializer(instance).data)


# ✅ 机器人接口
class RobotViewSet(viewsets.ModelViewSet):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUserOnly()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """获取机器人详细状态"""
        robot = self.get_object()
        
        # 获取当前订单
        current_orders = robot.get_current_orders()
        orders_data = []
        for order in current_orders:
            order_data = {
                "order_id": order.id,
                "status": order.status,
                "delivery_location": f"{order.delivery_building}-{order.delivery_room or '指定地点'}",
                "qr_is_valid": order.qr_is_valid,
                "qr_scanned_at": order.qr_scanned_at.isoformat() if order.qr_scanned_at else None
            }
            orders_data.append(order_data)
        
        return Response({
            "id": robot.id,
            "name": robot.name,
            "status": robot.status,
            "current_location": robot.current_location,
            "battery_level": robot.battery_level,
            "door_status": robot.door_status,
            "current_orders": orders_data,
            "last_update": robot.last_status_update.isoformat(),
            "delivery_start_time": robot.delivery_start_time.isoformat() if robot.delivery_start_time else None,
            "qr_wait_start_time": robot.qr_wait_start_time.isoformat() if robot.qr_wait_start_time else None
        })

    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        """发送控制指令给机器人"""
        robot = self.get_object()
        action = request.data.get('action')
        
        if not action:
            return Response({"detail": "请提供操作指令"}, status=400)
        
        try:
            # 创建控制指令记录
            command = RobotCommand.objects.create(
                robot=robot,
                command=action,
                status='PENDING',
                sent_by=request.user,
                sent_at=timezone.now()
            )
            
            # 记录控制指令（轮询模式下，机器人会定期检查命令）
            SystemLog.log_info(
                f"机器人 {robot.name} 收到指令: {action}",
                log_type='ROBOT_CONTROL',
                robot=robot,
                user=request.user,
                data={'command_id': command.id, 'action': action, 'method': 'polling'}
            )
            
            return Response({
                "message": f"控制指令已发送给机器人 {robot.name}，等待机器人执行",
                "command_id": command.id,
                "action": action,
                "status": "PENDING",
                "sent_at": command.sent_at.isoformat(),
                "method": "polling"
            })
                
        except Exception as e:
            SystemLog.log_error(
                f"发送控制指令失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot,
                user=request.user,
                data=request.data
            )
            return Response({"detail": f"发送指令失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def emergency_button(self, request, pk=None):
        """紧急按钮 - 立即开门并更新状态"""
        robot = self.get_object()
        
        try:
            # 立即更新门状态为开启
            robot.set_door_status('OPEN')
            
            # 创建紧急开门指令记录
            command = RobotCommand.objects.create(
                robot=robot,
                command='emergency_open_door',
                status='COMPLETED',  # 紧急指令立即完成
                sent_by=request.user,
                sent_at=timezone.now(),
                executed_at=timezone.now(),
                result='紧急按钮触发，门已立即开启'
            )
            
            # 记录紧急事件日志
            SystemLog.log_warning(
                f"🚨 紧急按钮触发！机器人 {robot.name} 的门已立即开启",
                log_type='ROBOT_CONTROL',
                robot=robot,
                user=request.user,
                data={
                    'command_id': command.id,
                    'action': 'emergency_open_door',
                    'door_status': 'OPEN',
                    'emergency': True
                }
            )
            
            return Response({
                "message": "🚨 紧急按钮已触发！门已立即开启",
                "command_id": command.id,
                "action": "emergency_open_door",
                "status": "COMPLETED",
                "door_status": "OPEN",
                "sent_at": command.sent_at.isoformat(),
                "executed_at": command.executed_at.isoformat(),
                "emergency": True
            })
                
        except Exception as e:
            SystemLog.log_error(
                f"紧急按钮操作失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot,
                data=request.data,
                user=request.user
            )
            return Response({"detail": f"紧急按钮操作失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['get'])
    def get_commands(self, request, pk=None):
        """机器人获取待执行的指令"""
        robot = self.get_object()
        
        try:
            from datetime import timedelta
            
            # 1. 自动处理超时的待执行命令（超过5分钟未执行）
            # 注意：紧急按钮命令不会被超时处理
            timeout_cutoff = timezone.now() - timedelta(minutes=5)
            timeout_commands = RobotCommand.objects.filter(
                robot=robot,
                status='PENDING',
                sent_at__lt=timeout_cutoff
            ).exclude(command='emergency_open_door')  # 排除紧急按钮命令
            
            timeout_count = 0
            for command in timeout_commands:
                command.status = 'FAILED'
                command.result = '命令执行超时'
                command.executed_at = timezone.now()
                command.save()
                timeout_count += 1
                
                SystemLog.log_warning(
                    f"命令执行超时: {command.command}",
                    log_type='ROBOT_CONTROL',
                    robot=robot,
                    data={'command_id': command.id, 'command': command.command}
                )
            
            # 2. 获取剩余的待执行指令
            pending_commands = RobotCommand.objects.filter(
                robot=robot,
                status='PENDING'
            ).order_by('sent_at')
            
            commands_data = []
            for command in pending_commands:
                commands_data.append({
                    'command_id': command.id,
                    'command': command.command,
                    'command_display': command.get_command_display(),
                    'sent_at': command.sent_at.isoformat(),
                    'sent_by': command.sent_by.username if command.sent_by else None
                })
            
            return Response({
                'robot_id': robot.id,
                'robot_name': robot.name,
                'pending_commands': commands_data,
                'command_count': len(commands_data),
                'timeout_processed': timeout_count
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"获取机器人指令失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot
            )
            return Response({"detail": f"获取指令失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def execute_command(self, request, pk=None):
        """机器人执行指令并报告结果"""
        robot = self.get_object()
        command_id = request.data.get('command_id')
        result = request.data.get('result', '')
        
        if not command_id:
            return Response({"detail": "请提供指令ID"}, status=400)
        
        try:
            command = RobotCommand.objects.get(id=command_id, robot=robot)
            
            if command.status != 'PENDING':
                return Response({"detail": "指令已被处理"}, status=400)
            
            # 更新指令状态
            command.status = 'COMPLETED'
            command.executed_at = timezone.now()
            command.result = result
            command.save()
            
            # 根据指令类型执行相应操作
            if command.command == 'open_door':
                # 从ROS返回的result中解析真实门状态
                if result and result.startswith('door_'):
                    door_state = result.replace('door_', '').upper()
                    if door_state in ['OPEN', 'CLOSED']:
                        robot.set_door_status(door_state)
                        SystemLog.log_success(
                            f"机器人 {robot.name} 执行开门指令成功，真实门状态: {door_state}",
                            log_type='ROBOT_CONTROL',
                            robot=robot,
                            data={'real_door_state': door_state, 'result': result}
                        )
                    else:
                        # 如果解析失败，使用默认状态
                        robot.set_door_status('OPEN')
                        SystemLog.log_warning(
                            f"机器人 {robot.name} 执行开门指令，但门状态解析失败: {result}",
                            log_type='ROBOT_CONTROL',
                            robot=robot,
                            data={'result': result}
                        )
                else:
                    # 如果没有返回门状态，使用默认状态
                    robot.set_door_status('OPEN')
                    SystemLog.log_success(
                        f"机器人 {robot.name} 执行开门指令成功",
                        log_type='ROBOT_CONTROL',
                        robot=robot
                    )
            elif command.command == 'close_door':
                # 从ROS返回的result中解析真实门状态
                if result and result.startswith('door_'):
                    door_state = result.replace('door_', '').upper()
                    if door_state in ['OPEN', 'CLOSED']:
                        robot.set_door_status(door_state)
                        SystemLog.log_success(
                            f"机器人 {robot.name} 执行关门指令成功，真实门状态: {door_state}",
                            log_type='ROBOT_CONTROL',
                            robot=robot,
                            data={'real_door_state': door_state, 'result': result}
                        )
                    else:
                        # 如果解析失败，使用默认状态
                        robot.set_door_status('CLOSED')
                        SystemLog.log_warning(
                            f"机器人 {robot.name} 执行关门指令，但门状态解析失败: {result}",
                            log_type='ROBOT_CONTROL',
                            robot=robot,
                            data={'result': result}
                        )
                else:
                    # 如果没有返回门状态，使用默认状态
                    robot.set_door_status('CLOSED')
                    SystemLog.log_success(
                        f"机器人 {robot.name} 执行关门指令成功",
                        log_type='ROBOT_CONTROL',
                        robot=robot
                    )
            elif command.command == 'start_delivery':
                if robot.status == 'LOADING':
                    robot.status = 'DELIVERING'
                    robot.delivery_start_time = timezone.now()
                    robot.save()
                    
                    # 更新所有分配给该机器人的订单状态为DELIVERING
                    assigned_orders = DeliveryOrder.objects.filter(
                        robot=robot,
                        status='ASSIGNED'
                    )
                    for order in assigned_orders:
                        order.status = 'DELIVERING'
                        order.save()
                    
                    SystemLog.log_success(
                        f"机器人 {robot.name} 执行开始配送指令成功",
                        log_type='DELIVERY',
                        robot=robot
                    )
            elif command.command == 'stop_robot':
                robot.status = 'IDLE'
                robot.delivery_start_time = None
                robot.qr_wait_start_time = None
                robot.save()
                
                # 将正在配送的订单状态重置为ASSIGNED
                delivering_orders = DeliveryOrder.objects.filter(
                    robot=robot,
                    status='DELIVERING'
                )
                for order in delivering_orders:
                    order.status = 'ASSIGNED'
                    order.save()
                
                SystemLog.log_warning(
                    f"机器人 {robot.name} 执行停止指令成功",
                    log_type='ROBOT_CONTROL',
                    robot=robot
                )
            
            return Response({
                "message": f"指令执行成功",
                "command_id": command_id,
                "status": "COMPLETED",
                "executed_at": command.executed_at.isoformat()
            })
            
        except RobotCommand.DoesNotExist:
            return Response({"detail": "指令不存在"}, status=404)
        except Exception as e:
            SystemLog.log_error(
                f"执行指令失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot,
                data=request.data
            )
            return Response({"detail": f"执行指令失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """机器人状态反馈API"""
        robot = self.get_object()
        
        try:
            # 更新位置
            location = request.data.get('location')
            if location:
                robot.update_location(location)
            
            # 更新电池
            battery = request.data.get('battery')
            if battery is not None:
                robot.update_battery(battery)
            
            # 更新门状态
            door_status = request.data.get('door_status')
            if door_status in ['OPEN', 'CLOSED']:
                robot.set_door_status(door_status)
            
            # 更新机器人状态
            status = request.data.get('status')
            if status in ['IDLE', 'LOADING', 'DELIVERING', 'MAINTENANCE', 'RETURNING']:
                robot.status = status
                robot.save()
            
            # 记录日志
            SystemLog.log_info(
                f"机器人 {robot.name} 状态更新: 位置={robot.current_location}, 电池={robot.battery_level}%, 门={robot.door_status}",
                log_type='ROBOT_CONTROL',
                robot=robot,
                data=request.data
            )
            
            return Response({
                "message": "状态更新成功",
                "robot_id": robot.id,
                "status": robot.status,
                "location": robot.current_location,
                "battery": robot.battery_level,
                "door_status": robot.door_status
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"机器人状态更新失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot,
                data=request.data
            )
            return Response({"detail": f"状态更新失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        """机器人心跳接口"""
        robot = self.get_object()
        
        try:
            # 更新机器人最后活动时间
            robot.last_status_update = timezone.now()
            robot.save()
            
            SystemLog.log_info(
                f"机器人 {robot.name} 心跳",
                log_type='ROBOT_CONTROL',
                robot=robot,
                data=request.data
            )
            
            return Response({
                'robot_id': robot.id,
                'robot_name': robot.name,
                'status': 'online',
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"机器人心跳处理失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot
            )
            return Response({"detail": f"心跳处理失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """机器人状态更新接口"""
        robot = self.get_object()
        
        try:
            # 更新机器人状态
            status_data = request.data.get('data', {})
            
            if 'battery' in status_data:
                robot.battery_level = status_data['battery']
            
            if 'location' in status_data:
                robot.current_location = status_data['location']
            
            if 'door_status' in status_data:
                door_status = status_data['door_status'].upper()
                if door_status in ['OPEN', 'CLOSED']:
                    robot.door_status = door_status
            
            robot.last_status_update = timezone.now()
            robot.save()
            
            SystemLog.log_info(
                f"机器人 {robot.name} 状态更新",
                log_type='ROBOT_CONTROL',
                robot=robot,
                data=status_data
            )
            
            return Response({
                'robot_id': robot.id,
                'robot_name': robot.name,
                'status': 'updated',
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"机器人状态更新失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot
            )
            return Response({"detail": f"状态更新失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def qr_scanned(self, request, pk=None):
        """二维码扫描处理API - 机器人扫描二维码后上报"""
        robot = self.get_object()
        qr_data = request.data.get('qr_data')
        
        if not qr_data:
            return Response({"detail": "请提供二维码数据"}, status=400)
        
        try:
            # 解析简单二维码数据
            if isinstance(qr_data, str):
                # 如果是字符串，尝试解析JSON
                try:
                    qr_json = json.loads(qr_data)
                except json.JSONDecodeError:
                    return Response({"detail": "二维码数据格式错误"}, status=400)
            else:
                qr_json = qr_data
            
            # 从二维码数据中提取订单信息
            order_id = qr_json.get("order_id")
            student_id = qr_json.get("student_id")
            
            if not order_id or not student_id:
                return Response({"detail": "二维码数据缺少必要字段"}, status=400)
            
            # 查找对应的订单
            try:
                order = DeliveryOrder.objects.get(id=order_id, student_id=student_id)
            except DeliveryOrder.DoesNotExist:
                return Response({"detail": "订单不存在或学生ID不匹配"}, status=404)
            
            # 验证二维码是否有效
            if not order.qr_is_valid:
                SystemLog.log_warning(
                    f"订单 {order_id} 二维码已失效",
                    log_type='QR_SCAN',
                    robot=robot,
                    order=order
                )
                return Response({"detail": "二维码已失效"}, status=400)
            
            # 更新订单状态为已取出
            order.status = 'PICKED_UP'
            order.qr_scanned_at = timezone.now()
            order.qr_is_valid = False  # 二维码失效
            order.save()
            
            # 更新机器人状态
            robot.qr_wait_start_time = None
            robot.save()
            
            SystemLog.log_success(
                f"订单 {order_id} 二维码扫描成功，包裹已取出",
                log_type='QR_SCAN',
                robot=robot,
                order=order,
                data={'qr_data': qr_data}
            )
            
            return Response({
                "message": f"订单 {order_id} 二维码扫描成功，包裹已取出",
                "order_id": order_id,
                "status": order.status,
                "qr_scanned_at": order.qr_scanned_at.isoformat()
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"二维码扫描处理失败: {str(e)}",
                log_type='QR_SCAN',
                robot=robot,
                data=request.data
            )
            return Response({"detail": f"处理失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def start_qr_wait(self, request, pk=None):
        """开始等待二维码扫描"""
        robot = self.get_object()
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({"detail": "请提供订单ID"}, status=400)
        
        try:
            order = DeliveryOrder.objects.get(id=order_id, robot=robot)
            
            # 设置等待开始时间
            robot.qr_wait_start_time = timezone.now()
            robot.save()
            
            SystemLog.log_info(
                f"订单 {order_id} 开始等待二维码扫描",
                log_type='QR_SCAN',
                robot=robot,
                order=order
            )
            
            return Response({
                "message": f"订单 {order_id} 开始等待二维码扫描",
                "qr_wait_start_time": robot.qr_wait_start_time.isoformat()
            })
            
        except DeliveryOrder.DoesNotExist:
            return Response({"detail": "订单不存在"}, status=404)
        except Exception as e:
            return Response({"detail": f"操作失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def arrived_at_destination(self, request, pk=None):
        """机器人到达目的地，自动更新订单状态为已送达"""
        robot = self.get_object()
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({"detail": "请提供订单ID"}, status=400)
        
        try:
            order = DeliveryOrder.objects.get(id=order_id, robot=robot)
            
            # 检查订单状态是否为DELIVERING
            if order.status != 'DELIVERING':
                return Response({"detail": "只有配送中的订单才能标记为已送达"}, status=400)
            
            # 更新订单状态为已送达
            order.status = 'DELIVERED'
            order.save()
            
            # 开始等待二维码扫描
            robot.qr_wait_start_time = timezone.now()
            robot.save()
            
            SystemLog.log_success(
                f"订单 {order_id} 机器人已到达目的地，状态更新为已送达",
                log_type='DELIVERY',
                robot=robot,
                order=order
            )
            
            return Response({
                "message": f"订单 {order_id} 已送达，等待用户扫描二维码",
                "order_id": order_id,
                "status": order.status,
                "qr_wait_start_time": robot.qr_wait_start_time.isoformat()
            })
            
        except DeliveryOrder.DoesNotExist:
            return Response({"detail": "订单不存在"}, status=404)
        except Exception as e:
            SystemLog.log_error(
                f"更新订单状态失败: {str(e)}",
                log_type='DELIVERY',
                robot=robot,
                data=request.data
            )
            return Response({"detail": f"操作失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def mark_picked_up(self, request, pk=None):
        """标记包裹已取出"""
        robot = self.get_object()
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({"detail": "请提供订单ID"}, status=400)
        
        try:
            order = DeliveryOrder.objects.get(id=order_id, robot=robot)
            
            # 检查订单状态是否为DELIVERED
            if order.status != 'DELIVERED':
                return Response({"detail": "只有已送达的订单才能标记为已取出"}, status=400)
            
            # 更新订单状态为已取出
            order.status = 'PICKED_UP'
            order.save()
            
            SystemLog.log_success(
                f"订单 {order_id} 标记为已取出",
                log_type='ORDER_STATUS',
                robot=robot,
                order=order
            )
            
            return Response({
                "message": f"订单 {order_id} 已标记为已取出",
                "order_id": order_id,
                "status": order.status
            })
            
        except DeliveryOrder.DoesNotExist:
            return Response({"detail": "订单不存在"}, status=404)
        except Exception as e:
            SystemLog.log_error(
                f"标记包裹取出失败: {str(e)}",
                log_type='ORDER_STATUS',
                robot=robot,
                data=request.data
            )
            return Response({"detail": f"操作失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def auto_return(self, request, pk=None):
        """自动返航（超时未取包裹）"""
        robot = self.get_object()
        
        try:
            # 查找所有已送达但未取出的订单，将其状态改为作废
            delivered_orders = DeliveryOrder.objects.filter(
                robot=robot,
                status='DELIVERED'
            )
            
            cancelled_orders = []
            for order in delivered_orders:
                order.status = 'CANCELLED'
                order.save()
                cancelled_orders.append(order)
                
                SystemLog.log_warning(
                    f"订单 #{order.id} 超时未取，状态更新为已作废",
                    log_type='ORDER_STATUS',
                    robot=robot,
                    order=order
                )
            
            # 更新机器人状态
            robot.status = 'RETURNING'
            robot.qr_wait_start_time = None
            robot.save()
            
            SystemLog.log_warning(
                f"机器人 {robot.name} 开始自动返航，{len(cancelled_orders)} 个订单因超时未取而作废",
                log_type='DELIVERY',
                robot=robot
            )
            
            return Response({
                "message": f"机器人 {robot.name} 开始自动返航",
                "status": robot.status,
                "cancelled_orders_count": len(cancelled_orders),
                "cancelled_orders": [order.id for order in cancelled_orders]
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"自动返航失败: {str(e)}",
                log_type='DELIVERY',
                robot=robot
            )
            return Response({"detail": f"自动返航失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['get'])
    def current_orders(self, request, pk=None):
        """获取机器人当前订单的完整信息"""
        robot = self.get_object()
        orders = robot.get_current_orders()
        
        # 构建订单详细信息
        orders_data = []
        for order in orders:
            order_data = {
                "order_id": order.id,
                "status": order.status,
                "student": {
                    "id": order.student.id,
                    "name": order.student.username,
                    "email": order.student.email,
                    "first_name": order.student.first_name,
                    "last_name": order.student.last_name,
                },
                "package_info": {
                    "type": order.package_type,
                    "weight": order.weight,
                    "fragile": order.fragile,
                    "description": order.description,
                },
                "pickup_location": {
                    "building": order.pickup_building,
                    "instructions": order.pickup_instructions,
                },
                "delivery_location": {
                    "building": order.delivery_building,
                    "room": order.delivery_room,
                },
                "qr_code_data": {
                    "payload": order.qr_payload_data,
                    "signature": order.qr_signature,
                    "qr_image_url": order.qr_code_url,
                },
                "delivery_priority": "normal",
                "estimated_time": "15分钟"
            }
            orders_data.append(order_data)
        
        # 生成配送路线
        delivery_route = []
        for i, order in enumerate(orders, 1):
            delivery_route.append({
                "sequence": i,
                "order_id": order.id,
                "location": f"{order.delivery_building}-{order.delivery_room or '指定地点'}",
                "estimated_arrival": "10:30"  # 这里可以根据实际路线计算
            })
        
        return Response({
            "robot_id": robot.id,
            "robot_name": robot.name,
            "status": robot.status,
            "current_orders": orders_data,
            "delivery_route": delivery_route,
            "summary": {
                "total_orders": len(orders),
                "loaded_orders": len([o for o in orders if o.status == 'DELIVERING']),
                "total_distance": "2.5km",  # 这里可以根据实际路线计算
                "estimated_total_time": f"{len(orders) * 15}分钟"
            }
        })

    @action(detail=True, methods=['post'])
    def receive_orders(self, request, pk=None):
        """接收订单分配给机器人 - 同时返回完整订单信息"""
        robot = self.get_object()
        order_ids = request.data.get('order_ids', [])
        
        if not order_ids:
            return Response({"detail": "请提供订单ID列表"}, status=400)
        
        try:
            orders = DeliveryOrder.objects.filter(id__in=order_ids, status='PENDING')
            if not orders.exists():
                return Response({"detail": "没有找到待分配的订单"}, status=400)
            
            # 更新订单状态和机器人关联
            orders.update(status='ASSIGNED', robot=robot)
            
            # 更新机器人状态
            robot.status = 'LOADING'
            robot.save()
            
            # 构建完整的订单信息数据（立即返回给机器人）
            orders_data = []
            for order in orders:
                order_data = {
                    "order_id": order.id,
                    "status": order.status,
                    "student": {
                        "id": order.student.id,
                        "name": order.student.username,
                        "email": order.student.email,
                        "first_name": order.student.first_name,
                        "last_name": order.student.last_name,
                    },
                    "package_info": {
                        "type": order.package_type,
                        "weight": order.weight,
                        "fragile": order.fragile,
                        "description": order.description,
                    },
                    "pickup_location": {
                        "building": order.pickup_building,
                        "instructions": order.pickup_instructions,
                    },
                    "delivery_location": {
                        "building": order.delivery_building,
                        "room": order.delivery_room,
                    },
                    "qr_code_data": {
                        "payload": order.qr_payload_data,
                        "signature": order.qr_signature,
                        "qr_image_url": order.qr_code_url,
                    },
                    "delivery_priority": "normal",
                    "estimated_time": "15分钟"
                }
                orders_data.append(order_data)
            
            # 生成配送路线
            delivery_route = []
            for i, order in enumerate(orders, 1):
                delivery_route.append({
                    "sequence": i,
                    "order_id": order.id,
                    "location": f"{order.delivery_building}-{order.delivery_room or '指定地点'}",
                    "estimated_arrival": "10:30"
                })
            
            return Response({
                "detail": f"成功分配 {orders.count()} 个订单给机器人 {robot.name}",
                "robot_id": robot.id,
                "robot_name": robot.name,
                "status": robot.status,
                "assigned_orders": list(orders.values_list('id', flat=True)),
                # 立即返回完整的订单信息给机器人
                "current_orders": orders_data,
                "delivery_route": delivery_route,
                "summary": {
                    "total_orders": len(orders),
                    "loaded_orders": 0,  # 刚开始装货，已装货数量为0
                    "total_distance": "2.5km",
                    "estimated_total_time": f"{len(orders) * 15}分钟"
                }
            })
            
        except Exception as e:
            return Response({"detail": f"分配订单失败: {str(e)}"}, status=400)

    @action(detail=True, methods=['post'])
    def start_delivery(self, request, pk=None):
        """机器人开始配送"""
        robot = self.get_object()
        action = request.data.get('action')
        
        if action != 'close_door_and_start':
            return Response({"detail": "无效的操作"}, status=400)
        
        # 检查是否有待配送的订单
        current_orders = robot.get_current_orders()
        if not current_orders.exists():
            return Response({"detail": "没有待配送的订单"}, status=400)
        
        # 更新机器人状态
        robot.status = 'DELIVERING'
        robot.save()
        
        return Response({
            "detail": "机器人已开始配送",
            "robot_id": robot.id,
            "status": robot.status,
            "total_orders": current_orders.count()
        })

    @action(detail=True, methods=['post'])
    def clear_completed_commands(self, request, pk=None):
        """清理已完成的命令"""
        robot = self.get_object()
        
        try:
            # 获取已完成的命令数量
            completed_count = RobotCommand.objects.filter(
                robot=robot,
                status__in=['COMPLETED', 'FAILED', 'CANCELLED']
            ).count()
            
            # 删除已完成的命令（保留最近7天的）
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=7)
            
            deleted_count = RobotCommand.objects.filter(
                robot=robot,
                status__in=['COMPLETED', 'FAILED', 'CANCELLED'],
                sent_at__lt=cutoff_date
            ).delete()[0]
            
            SystemLog.log_info(
                f"清理机器人 {robot.name} 的已完成命令",
                log_type='ROBOT_CONTROL',
                robot=robot,
                user=request.user,
                data={'deleted_count': deleted_count, 'total_completed': completed_count}
            )
            
            return Response({
                "message": f"已清理 {deleted_count} 个已完成命令",
                "deleted_count": deleted_count,
                "total_completed": completed_count
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"清理已完成命令失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot,
                user=request.user
            )
            return Response({"detail": f"清理失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def cleanup_command_queue(self, request, pk=None):
        """清理命令队列 - 自动清理已完成和超时命令"""
        robot = self.get_object()
        
        try:
            from datetime import timedelta
            
            # 1. 清理已完成的命令（保留最近3天）
            completed_cutoff = timezone.now() - timedelta(days=3)
            completed_deleted = RobotCommand.objects.filter(
                robot=robot,
                status__in=['COMPLETED', 'FAILED', 'CANCELLED'],
                sent_at__lt=completed_cutoff
            ).delete()[0]
            
            # 2. 处理超时的待执行命令（超过5分钟未执行）
            # 注意：紧急按钮命令不会被超时处理
            timeout_cutoff = timezone.now() - timedelta(minutes=5)
            timeout_commands = RobotCommand.objects.filter(
                robot=robot,
                status='PENDING',
                sent_at__lt=timeout_cutoff
            ).exclude(command='emergency_open_door')  # 排除紧急按钮命令
            
            timeout_count = timeout_commands.count()
            for command in timeout_commands:
                command.status = 'FAILED'
                command.result = '命令执行超时'
                command.executed_at = timezone.now()
                command.save()
                
                SystemLog.log_warning(
                    f"命令执行超时: {command.command}",
                    log_type='ROBOT_CONTROL',
                    robot=robot,
                    user=request.user,
                    data={'command_id': command.id, 'command': command.command}
                )
            
            # 3. 清理超时的失败命令（保留最近1天）
            failed_cutoff = timezone.now() - timedelta(days=1)
            failed_deleted = RobotCommand.objects.filter(
                robot=robot,
                status='FAILED',
                sent_at__lt=failed_cutoff
            ).delete()[0]
            
            total_deleted = completed_deleted + failed_deleted
            
            SystemLog.log_info(
                f"清理机器人 {robot.name} 的命令队列",
                log_type='ROBOT_CONTROL',
                robot=robot,
                user=request.user,
                data={
                    'completed_deleted': completed_deleted,
                    'timeout_commands': timeout_count,
                    'failed_deleted': failed_deleted,
                    'total_deleted': total_deleted
                }
            )
            
            return Response({
                "message": f"命令队列清理完成",
                "completed_deleted": completed_deleted,
                "timeout_commands": timeout_count,
                "failed_deleted": failed_deleted,
                "total_deleted": total_deleted
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"清理命令队列失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot,
                user=request.user
            )
            return Response({"detail": f"清理失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['get'])
    def emergency_events(self, request, pk=None):
        """获取最近的紧急按钮事件"""
        robot = self.get_object()
        
        try:
            from datetime import timedelta
            
            # 获取最近1分钟内的紧急按钮事件
            one_minute_ago = timezone.now() - timedelta(minutes=1)
            
            # 从系统日志中查找紧急按钮事件
            emergency_logs = SystemLog.objects.filter(
                log_type='ROBOT_CONTROL',
                robot=robot,
                timestamp__gte=one_minute_ago,
                message__icontains='紧急按钮'
            ).order_by('-timestamp')[:5]
            
            events = []
            for log in emergency_logs:
                events.append({
                    'id': log.id,
                    'message': log.message,
                    'timestamp': log.timestamp.isoformat(),
                    'level': log.level,
                    'data': log.data
                })
            
            return Response({
                'robot_id': robot.id,
                'robot_name': robot.name,
                'emergency_events': events,
                'event_count': len(events),
                'last_check': timezone.now().isoformat()
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"获取紧急按钮事件失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot
            )
            return Response({"detail": f"获取事件失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['get'])
    def command_events(self, request, pk=None):
        """获取最近的命令事件"""
        robot = self.get_object()
        
        try:
            from datetime import timedelta
            
            # 获取最近2分钟内的命令事件
            two_minutes_ago = timezone.now() - timedelta(minutes=2)
            
            # 从系统日志中查找命令事件
            command_logs = SystemLog.objects.filter(
                log_type='ROBOT_CONTROL',
                robot=robot,
                timestamp__gte=two_minutes_ago
            ).order_by('-timestamp')[:10]
            
            events = []
            for log in command_logs:
                events.append({
                    'id': log.id,
                    'message': log.message,
                    'timestamp': log.timestamp.isoformat(),
                    'level': log.level,
                    'data': log.data
                })
            
            return Response({
                'robot_id': robot.id,
                'robot_name': robot.name,
                'command_events': events,
                'event_count': len(events),
                'last_check': timezone.now().isoformat()
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"获取命令事件失败: {str(e)}",
                log_type='ROBOT_CONTROL',
                robot=robot
            )
            return Response({"detail": f"获取事件失败: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def upload_qr_image(self, request, pk=None):
        """机器人上传二维码图片进行识别"""
        robot = self.get_object()
        image = request.FILES.get('qr_image')
        
        if not image:
            return Response({"detail": "请上传二维码图片"}, status=400)
        
        try:
            # 使用PIL和pyzbar识别二维码
            img = Image.open(image)
            qr_data_list = decode(img)
            
            if not qr_data_list:
                SystemLog.log_warning(
                    f"机器人 {robot.name} 上传的二维码图片无法识别",
                    log_type='QR_SCAN',
                    robot=robot,
                    data={'image_name': image.name}
                )
                return Response({"detail": "无法识别二维码，请重新拍照"}, status=400)
            
            # 解析简单二维码数据
            try:
                data = qr_data_list[0].data.decode("utf-8")
                qr_json = json.loads(data)
            except Exception as e:
                SystemLog.log_error(
                    f"二维码数据解析失败: {str(e)}",
                    log_type='QR_SCAN',
                    robot=robot,
                    data={'image_name': image.name, 'raw_data': data}
                )
                return Response({"detail": f"二维码数据格式错误: {str(e)}"}, status=400)
            
            # 提取订单信息
            order_id = qr_json.get("order_id")
            student_id = qr_json.get("student_id")
            
            if not order_id or not student_id:
                return Response({"detail": "二维码数据缺少必要字段"}, status=400)
            
            # 查找对应的订单
            try:
                order = DeliveryOrder.objects.get(id=order_id, student_id=student_id)
            except DeliveryOrder.DoesNotExist:
                SystemLog.log_warning(
                    f"机器人 {robot.name} 扫描的二维码对应订单不存在",
                    log_type='QR_SCAN',
                    robot=robot,
                    data={'order_id': order_id, 'student_id': student_id}
                )
                return Response({"detail": "订单不存在或学生ID不匹配"}, status=404)
            
            # 验证二维码是否有效
            if not order.qr_is_valid:
                SystemLog.log_warning(
                    f"机器人 {robot.name} 扫描的二维码已失效",
                    log_type='QR_SCAN',
                    robot=robot,
                    order=order
                )
                return Response({"detail": "二维码已失效，请使用新的二维码"}, status=400)
            
            # 更新订单状态为已取出
            order.status = 'PICKED_UP'
            order.qr_scanned_at = timezone.now()
            order.qr_is_valid = False  # 二维码失效
            order.save()
            
            # 更新机器人状态
            robot.qr_wait_start_time = None
            robot.save()
            
            SystemLog.log_success(
                f"机器人 {robot.name} 成功扫描二维码，订单 {order_id} 包裹已取出",
                log_type='QR_SCAN',
                robot=robot,
                order=order,
                data={'image_name': image.name}
            )
            
            return Response({
                "message": f"二维码扫描成功！订单 {order_id} 包裹已取出",
                "order_id": order_id,
                "status": order.status,
                "qr_scanned_at": order.qr_scanned_at.isoformat(),
                "student_name": order.student.username
            })
            
        except Exception as e:
            SystemLog.log_error(
                f"机器人 {robot.name} 二维码图片处理失败: {str(e)}",
                log_type='QR_SCAN',
                robot=robot,
                data={'image_name': image.name if image else 'unknown'}
            )
            return Response({"detail": f"图片处理失败: {str(e)}"}, status=500)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    """系统日志视图集"""
    serializer_class = MessageSerializer  # 临时使用，需要创建专门的序列化器
    permission_classes = [IsAdminUserOnly]
    
    def get_queryset(self):
        queryset = SystemLog.objects.all()
        
        # 过滤条件
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        log_type = self.request.query_params.get('log_type')
        if log_type:
            queryset = queryset.filter(log_type=log_type)
        
        robot_id = self.request.query_params.get('robot_id')
        if robot_id:
            queryset = queryset.filter(robot_id=robot_id)
        
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # 时间范围过滤
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取日志统计摘要"""
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # 获取最近24小时的日志
        yesterday = datetime.now() - timedelta(days=1)
        recent_logs = SystemLog.objects.filter(timestamp__gte=yesterday)
        
        summary = {
            'total_logs': SystemLog.objects.count(),
            'recent_logs_24h': recent_logs.count(),
            'by_level': dict(recent_logs.values('level').annotate(count=Count('id')).values_list('level', 'count')),
            'by_type': dict(recent_logs.values('log_type').annotate(count=Count('id')).values_list('log_type', 'count')),
            'recent_errors': recent_logs.filter(level='ERROR').count(),
            'recent_warnings': recent_logs.filter(level='WARNING').count(),
        }
        
        return Response(summary)


class QRCodeVerifyView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        image = request.FILES.get('file')
        print("🖼️ 收到上传文件：", image.name if image else "无文件")

        if not image:
            return Response({"error_code": 1001, "detail": "未上传二维码图片"}, status=400)

        try:
            img = Image.open(image)
            qr_data_list = decode(img)
            print("🔍 二维码识别结果：", qr_data_list)

            if not qr_data_list:
                return Response({"error_code": 1002, "detail": "无法识别二维码"}, status=400)

            try:
                data = qr_data_list[0].data.decode("utf-8")
                print("📦 原始二维码内容：", data)
                qr_json = json.loads(data)
            except Exception as e:
                print("❌ 二维码数据解析失败：", e)
                return Response({"error_code": 1003, "detail": f"二维码数据解析失败: {str(e)}"}, status=400)

            payload_b64 = qr_json.get("payload")
            signature = qr_json.get("signature")
            print("📦 payload（base64）: ", payload_b64)
            print("🔏 signature: ", signature)

            if not payload_b64 or not signature:
                return Response({"error_code": 1004, "detail": "二维码数据格式不完整"}, status=400)

            try:
                payload_str = base64.b64decode(payload_b64).decode()
                print("📄 解码后的 payload：", payload_str)
            except Exception as e:
                print("❌ payload 解码失败：", e)
                return Response({"error_code": 1005, "detail": "payload 解码失败"}, status=400)

            expected_signature = hashlib.sha256((payload_str + settings.SECRET_KEY).encode()).hexdigest()
            print("🧮 校验签名：", expected_signature == signature)

            if signature != expected_signature:
                return Response({"error_code": 1006, "detail": "签名校验失败"}, status=403)

            try:
                payload = json.loads(payload_str)
                order_id = payload.get("order_id")
                student_id = payload.get("student_id")
                print("📋 提取 payload 字段：order_id =", order_id, "student_id =", student_id)
            except Exception as e:
                print("❌ payload 内容解析失败：", e)
                return Response({"error_code": 1007, "detail": "payload 内容解析失败"}, status=400)

            if not order_id or not student_id:
                return Response({"error_code": 1008, "detail": "payload 缺少必要字段"}, status=400)

            try:
                order = DeliveryOrder.objects.get(id=order_id, student_id=student_id)
                print("✅ 找到订单：", order.id)
            except DeliveryOrder.DoesNotExist:
                print("❌ 订单不存在或 student_id 不匹配")
                return Response({"error_code": 1009, "detail": "订单不存在或 student_id 不匹配"}, status=404)

            order.status = "DELIVERED"
            order.save()
            print("🚚 状态已更新为已送达")

            return Response({
                "detail": "✅ 验证成功，状态已更新为已送达",
                "order_id": order.id,
                "new_status": order.status,
            })

        except Exception as e:
            print("🔥 未知异常：", type(e).__name__, str(e))
            return Response({
                "error_code": 1999,
                "detail": f"服务器内部错误: {type(e).__name__}: {str(e)}"
            }, status=500)


class NetworkMonitorViewSet(viewsets.ReadOnlyModelViewSet):
    """网络监控视图集 - 实时查看所有网络活动"""
    permission_classes = [IsAdminUserOnly]
    
    def get_queryset(self):
        """获取网络相关的日志"""
        from .models import SystemLog
        
        # 获取查询参数
        log_type = self.request.query_params.get('log_type', '')
        client_ip = self.request.query_params.get('client_ip', '')
        user_id = self.request.query_params.get('user_id', '')
        limit = int(self.request.query_params.get('limit', 100))
        
        queryset = SystemLog.objects.filter(
            log_type__in=['NETWORK_REQUEST', 'NETWORK_RESPONSE', 'NETWORK_ERROR', 'WEBSOCKET_CONNECTION']
        )
        
        # 按类型过滤
        if log_type:
            queryset = queryset.filter(log_type=log_type)
        
        # 按IP过滤
        if client_ip:
            queryset = queryset.filter(data__client_ip__icontains=client_ip)
        
        # 按用户过滤
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-timestamp')[:limit]
    
    def list(self, request, *args, **kwargs):
        """获取网络监控数据"""
        queryset = self.get_queryset()
        
        # 序列化数据
        logs_data = []
        for log in queryset:
            log_data = {
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'level': log.level,
                'log_type': log.log_type,
                'message': log.message,
                'user': {
                    'id': log.user.id,
                    'username': log.user.username
                } if log.user else None,
                'data': log.data,
            }
            logs_data.append(log_data)
        
        # 统计信息
        total_requests = SystemLog.objects.filter(log_type='NETWORK_REQUEST').count()
        total_responses = SystemLog.objects.filter(log_type='NETWORK_RESPONSE').count()
        total_errors = SystemLog.objects.filter(log_type='NETWORK_ERROR').count()
        total_websockets = SystemLog.objects.filter(log_type='WEBSOCKET_CONNECTION').count()
        
        # 获取最近的活跃用户
        recent_users = SystemLog.objects.filter(
            log_type__in=['NETWORK_REQUEST', 'NETWORK_RESPONSE'],
            user__isnull=False
        ).values('user__id', 'user__username').distinct()[:10]
        
        # 获取最近的客户端IP
        recent_ips = SystemLog.objects.filter(
            log_type__in=['NETWORK_REQUEST', 'NETWORK_RESPONSE']
        ).values_list('data__client_ip', flat=True).distinct()[:10]
        
        response_data = {
            'logs': logs_data,
            'statistics': {
                'total_requests': total_requests,
                'total_responses': total_responses,
                'total_errors': total_errors,
                'total_websockets': total_websockets,
            },
            'recent_users': list(recent_users),
            'recent_ips': list(recent_ips),
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def realtime(self, request):
        """实时网络监控 - 获取最新的网络活动"""
        from django.utils import timezone
        from datetime import timedelta
        
        # 获取最近5分钟的网络活动
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        
        recent_logs = SystemLog.objects.filter(
            log_type__in=['NETWORK_REQUEST', 'NETWORK_RESPONSE', 'NETWORK_ERROR', 'WEBSOCKET_CONNECTION'],
            timestamp__gte=five_minutes_ago
        ).order_by('-timestamp')[:50]
        
        logs_data = []
        for log in recent_logs:
            log_data = {
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'level': log.level,
                'log_type': log.log_type,
                'message': log.message,
                'user': {
                    'id': log.user.id,
                    'username': log.user.username
                } if log.user else None,
                'data': log.data,
            }
            logs_data.append(log_data)
        
        return Response({
            'logs': logs_data,
            'last_update': timezone.now().isoformat(),
        })
    
    @action(detail=False, methods=['get'])
    def connections(self, request):
        """获取当前活跃连接"""
        from django.utils import timezone
        from datetime import timedelta
        
        # 获取最近1分钟的网络请求（模拟活跃连接）
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        
        # 获取活跃连接，按IP分组，获取每个IP的最新活动时间
        active_connections_raw = SystemLog.objects.filter(
            log_type='NETWORK_REQUEST',
            timestamp__gte=one_minute_ago
        ).values('data__client_ip', 'user__username', 'timestamp')
        
        # 按IP去重，保留最新的活动时间
        connections_dict = {}
        for conn in active_connections_raw:
            client_ip = conn['data__client_ip']
            if client_ip:
                # 从data字段中获取timestamp，如果没有则使用当前时间
                timestamp = conn.get('timestamp') or timezone.now()
                if client_ip not in connections_dict or timestamp > connections_dict[client_ip]['timestamp']:
                    connections_dict[client_ip] = {
                        'client_ip': client_ip,
                        'username': conn['user__username'] or 'Anonymous',
                        'last_activity': timestamp.isoformat(),
                        'timestamp': timestamp,
                    }
        
        connections_data = list(connections_dict.values())
        
        return Response({
            'active_connections': connections_data,
            'total_connections': len(connections_data),
        })
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """获取用户活动统计"""
        from django.utils import timezone
        from datetime import timedelta
        
        # 获取最近24小时的用户活动
        one_day_ago = timezone.now() - timedelta(hours=24)
        
        user_activity = SystemLog.objects.filter(
            log_type__in=['NETWORK_REQUEST', 'NETWORK_RESPONSE'],
            user__isnull=False,
            timestamp__gte=one_day_ago
        ).values('user__id', 'user__username').annotate(
            request_count=Count('id', filter=Q(log_type='NETWORK_REQUEST')),
            response_count=Count('id', filter=Q(log_type='NETWORK_RESPONSE')),
        ).order_by('-request_count')[:20]
        
        return Response({
            'user_activity': list(user_activity),
            'period': '24小时',
        })
