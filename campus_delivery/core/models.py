import logging
from django.db import models
from django.utils import timezone

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_dispatcher = models.BooleanField(default=False)  # ✅ 快递管理员

    def __str__(self):
        return self.username


class DeliveryOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', '待分配'),
        ('ASSIGNED', '已装入机器人'),
        ('DELIVERING', '配送中'),
        ('DELIVERED', '已送达'),
        ('PICKED_UP', '已取出'),  # 新增：已取出状态
        ('CANCELLED', '已作废'),  # 新增：作废状态（超时未取）
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    teacher = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_orders')
    created_at = models.DateTimeField(auto_now_add=True)

    # 📦 包裹信息
    package_type = models.CharField(max_length=50)
    weight = models.CharField(max_length=20)
    fragile = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    # 🚚 取件与投递
    pickup_building = models.CharField(max_length=100)
    pickup_instructions = models.CharField(max_length=255, blank=True, null=True)
    delivery_building = models.CharField(max_length=100)
    delivery_room = models.CharField(max_length=20, blank=True, null=True)  # 新增：具体房间号

    # 🕓 配送调度
    delivery_speed = models.CharField(max_length=20)
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)

    # 📌 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # 🤖 机器人关联
    robot = models.ForeignKey('Robot', null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')

    # 🔐 二维码相关
    qr_code_url = models.TextField(blank=True, null=True)
    qr_payload_data = models.TextField(blank=True, null=True)  # 新增：存储解码后的payload
    qr_signature = models.CharField(max_length=64, blank=True, null=True)  # 新增：存储签名
    qr_scanned_at = models.DateTimeField(null=True, blank=True)  # 新增：二维码扫描时间
    qr_is_valid = models.BooleanField(default=True)  # 新增：二维码是否有效

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


class Robot(models.Model):
    STATUS_CHOICES = [
        ('IDLE', '空闲'),
        ('LOADING', '装货中'),
        ('DELIVERING', '配送中'),
        ('MAINTENANCE', '维护中'),
        ('RETURNING', '返航中'),  # 新增：返航状态
    ]
    
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IDLE')
    is_available = models.BooleanField(default=True)
    next_available_time = models.DateTimeField(null=True, blank=True)
    
    # 新增：机器人实时状态
    current_location = models.CharField(max_length=100, default='Warehouse')  # 当前位置
    battery_level = models.IntegerField(default=100)  # 电池电量
    door_status = models.CharField(max_length=20, choices=[
        ('OPEN', '开门'),
        ('CLOSED', '关门'),
    ], default='CLOSED')
    last_status_update = models.DateTimeField(auto_now=True)  # 最后状态更新时间
    
    # 新增：配送相关
    current_delivery_location = models.CharField(max_length=100, blank=True, null=True)  # 当前配送地点
    delivery_start_time = models.DateTimeField(null=True, blank=True)  # 配送开始时间
    qr_wait_start_time = models.DateTimeField(null=True, blank=True)  # 等待扫码开始时间

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    def get_current_orders(self):
        """获取当前机器人的所有订单"""
        return DeliveryOrder.objects.filter(
            status__in=['ASSIGNED', 'DELIVERING'],
            robot=self
        )
    
    def update_location(self, location):
        """更新机器人位置"""
        self.current_location = location
        self.last_status_update = timezone.now()
        self.save()
    
    def update_battery(self, level):
        """更新电池电量"""
        self.battery_level = max(0, min(100, level))
        self.last_status_update = timezone.now()
        self.save()
    
    def set_door_status(self, status):
        """设置门状态"""
        self.door_status = status
        self.last_status_update = timezone.now()
        self.save()


class RobotCommand(models.Model):
    """机器人控制指令模型"""
    COMMAND_TYPES = [
        ('open_door', '开门'),
        ('close_door', '关门'),
        ('start_delivery', '开始配送'),
        ('stop_robot', '停止机器人'),
        ('arrived_at_destination', '到达目的地'),
        ('auto_return', '自动返航'),
        ('emergency_open_door', '紧急开门'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', '待执行'),
        ('EXECUTING', '执行中'),
        ('COMPLETED', '已完成'),
        ('FAILED', '执行失败'),
        ('CANCELLED', '已取消'),
    ]
    
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='commands')
    command = models.CharField(max_length=50, choices=COMMAND_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = '机器人指令'
        verbose_name_plural = '机器人指令'
    
    def __str__(self):
        return f"机器人{self.robot.name} - {self.get_command_display()} - {self.status}"


class SystemLog(models.Model):
    """系统日志模型"""
    LOG_LEVEL_CHOICES = [
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
        ('SUCCESS', '成功'),
    ]
    
    LOG_TYPE_CHOICES = [
        ('ROBOT_CONTROL', '机器人控制'),
        ('ORDER_STATUS', '订单状态'),
        ('QR_SCAN', '二维码扫描'),
        ('SYSTEM', '系统'),
        ('DELIVERY', '配送'),
        ('NETWORK_REQUEST', '网络请求'),
        ('NETWORK_RESPONSE', '网络响应'),
        ('NETWORK_ERROR', '网络错误'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, default='INFO')
    log_type = models.CharField(max_length=50, choices=LOG_TYPE_CHOICES, default='SYSTEM')
    message = models.TextField()
    
    # 关联对象
    robot = models.ForeignKey(Robot, null=True, blank=True, on_delete=models.CASCADE)
    order = models.ForeignKey(DeliveryOrder, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    
    # 额外数据
    data = models.JSONField(default=dict, blank=True)  # 存储额外的JSON数据
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['level']),
            models.Index(fields=['log_type']),
        ]
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.level} - {self.message[:50]}"
    
    @classmethod
    def log_info(cls, message, log_type='SYSTEM', robot=None, order=None, user=None, data=None):
        """记录信息日志"""
        # 创建数据库记录
        log_entry = cls.objects.create(
            level='INFO',
            log_type=log_type,
            message=message,
            robot=robot,
            order=order,
            user=user,
            data=data or {}
        )
        
        # 同时写入日志文件
        logger = logging.getLogger('system_backend')
        robot_info = f" (机器人: {robot.name})" if robot else ""
        order_info = f" (订单: #{order.id})" if order else ""
        user_info = f" (用户: {user.username})" if user else ""
        log_message = f"[{log_type}] {message}{robot_info}{order_info}{user_info}"
        logger.info(log_message)
        
        return log_entry
    
    @classmethod
    def log_warning(cls, message, log_type='SYSTEM', robot=None, order=None, user=None, data=None):
        """记录警告日志"""
        # 创建数据库记录
        log_entry = cls.objects.create(
            level='WARNING',
            log_type=log_type,
            message=message,
            robot=robot,
            order=order,
            user=user,
            data=data or {}
        )
        
        # 同时写入日志文件
        logger = logging.getLogger('system_backend')
        robot_info = f" (机器人: {robot.name})" if robot else ""
        order_info = f" (订单: #{order.id})" if order else ""
        user_info = f" (用户: {user.username})" if user else ""
        log_message = f"[{log_type}] {message}{robot_info}{order_info}{user_info}"
        logger.warning(log_message)
        
        return log_entry
    
    @classmethod
    def log_error(cls, message, log_type='SYSTEM', robot=None, order=None, user=None, data=None):
        """记录错误日志"""
        # 创建数据库记录
        log_entry = cls.objects.create(
            level='ERROR',
            log_type=log_type,
            message=message,
            robot=robot,
            order=order,
            user=user,
            data=data or {}
        )
        
        # 同时写入日志文件
        logger = logging.getLogger('system_backend')
        robot_info = f" (机器人: {robot.name})" if robot else ""
        order_info = f" (订单: #{order.id})" if order else ""
        user_info = f" (用户: {user.username})" if user else ""
        log_message = f"[{log_type}] {message}{robot_info}{order_info}{user_info}"
        logger.error(log_message)
        
        return log_entry
    
    @classmethod
    def log_success(cls, message, log_type='SYSTEM', robot=None, order=None, user=None, data=None):
        """记录成功日志"""
        # 创建数据库记录
        log_entry = cls.objects.create(
            level='SUCCESS',
            log_type=log_type,
            message=message,
            robot=robot,
            order=order,
            user=user,
            data=data or {}
        )
        
        # 同时写入日志文件
        logger = logging.getLogger('system_backend')
        robot_info = f" (机器人: {robot.name})" if robot else ""
        order_info = f" (订单: #{order.id})" if order else ""
        user_info = f" (用户: {user.username})" if user else ""
        log_message = f"[{log_type}] {message}{robot_info}{order_info}{user_info}"
        logger.info(log_message)  # 成功日志也使用INFO级别写入文件
        
        return log_entry


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


