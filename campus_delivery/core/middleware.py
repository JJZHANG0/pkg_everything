import json
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .models import SystemLog
from django.utils import timezone

logger = logging.getLogger('system_backend')

class NetworkMonitorMiddleware(MiddlewareMixin):
    """网络监控中间件 - 记录所有HTTP请求和响应"""
    
    def process_request(self, request):
        """处理请求 - 记录请求信息"""
        # 记录请求开始时间
        request.start_time = time.time()
        
        # 获取客户端信息
        client_ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        method = request.method
        path = request.path
        query_params = dict(request.GET.items())
        
        # 获取请求体（如果是POST/PUT等）
        request_body = {}
        if method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json':
                    request_body = json.loads(request.body.decode('utf-8'))
                else:
                    request_body = dict(request.POST.items())
            except:
                request_body = {'raw_body': str(request.body)}
        
        # 获取用户信息（安全检查）
        user_info = 'Anonymous'
        user_obj = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
            user_obj = request.user
        
        # 记录请求日志
        request_data = {
            'client_ip': client_ip,
            'user_agent': user_agent,
            'method': method,
            'path': path,
            'query_params': query_params,
            'request_body': request_body,
            'user': user_info,
            'timestamp': timezone.now().isoformat(),
        }
        
        # 保存到数据库
        try:
            SystemLog.log_info(
                message=f"收到请求: {method} {path}",
                log_type='NETWORK_REQUEST',
                user=user_obj,
                data=request_data
            )
        except Exception as e:
            logger.error(f"记录请求日志失败: {e}")
        
        # 同时记录到控制台
        logger.info(f"🌐 网络请求: {client_ip} - {user_info} - {method} {path}")
        
        return None
    
    def process_response(self, request, response):
        """处理响应 - 记录响应信息"""
        # 计算请求处理时间
        if hasattr(request, 'start_time'):
            processing_time = time.time() - request.start_time
        else:
            processing_time = 0
        
        # 获取响应信息
        status_code = response.status_code
        content_length = len(response.content) if hasattr(response, 'content') else 0
        
        # 获取响应体（如果是JSON响应）
        response_body = {}
        if hasattr(response, 'content') and response.content:
            try:
                if response.get('Content-Type', '').startswith('application/json'):
                    response_body = json.loads(response.content.decode('utf-8'))
            except:
                response_body = {'raw_content': str(response.content)[:200]}
        
        # 获取用户信息（安全检查）
        user_info = 'Anonymous'
        user_obj = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
            user_obj = request.user
        
        # 记录响应日志
        response_data = {
            'status_code': status_code,
            'processing_time': round(processing_time, 3),
            'content_length': content_length,
            'response_body': response_body,
            'timestamp': timezone.now().isoformat(),
        }
        
        # 根据状态码选择日志级别
        if status_code >= 400:
            log_method = SystemLog.log_warning
            log_level = 'WARNING'
        else:
            log_method = SystemLog.log_info
            log_level = 'INFO'
        
        # 保存到数据库
        try:
            log_method(
                message=f"响应完成: {request.method} {request.path} - {status_code} ({processing_time:.3f}s)",
                log_type='NETWORK_RESPONSE',
                user=user_obj,
                data=response_data
            )
        except Exception as e:
            logger.error(f"记录响应日志失败: {e}")
        
        # 同时记录到控制台
        logger.info(f"📤 网络响应: {user_info} - {request.method} {request.path} - {status_code} ({processing_time:.3f}s)")
        
        return response
    
    def process_exception(self, request, exception):
        """处理异常 - 记录错误信息"""
        # 获取客户端信息
        client_ip = self.get_client_ip(request)
        user_info = 'Anonymous'
        user_obj = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
            user_obj = request.user
        
        # 记录异常日志
        exception_data = {
            'client_ip': client_ip,
            'method': request.method,
            'path': request.path,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'timestamp': timezone.now().isoformat(),
        }
        
        # 保存到数据库
        try:
            SystemLog.log_error(
                message=f"请求异常: {request.method} {request.path} - {type(exception).__name__}: {str(exception)}",
                log_type='NETWORK_ERROR',
                user=user_obj,
                data=exception_data
            )
        except Exception as e:
            logger.error(f"记录异常日志失败: {e}")
        
        # 同时记录到控制台
        logger.error(f"❌ 网络异常: {client_ip} - {user_info} - {request.method} {request.path} - {exception}")
        
        return None
    
    def get_client_ip(self, request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RealTimeMonitorMiddleware(MiddlewareMixin):
    """实时监控中间件 - 用于WebSocket连接监控"""
    
    def process_request(self, request):
        """处理WebSocket连接请求"""
        if 'websocket' in request.META.get('HTTP_UPGRADE', '').lower():
            client_ip = self.get_client_ip(request)
            user_info = 'Anonymous'
            user_obj = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = f"{request.user.username} (ID: {request.user.id})"
                user_obj = request.user
            
            # 记录WebSocket连接
            try:
                SystemLog.log_info(
                    message=f"WebSocket连接建立: {client_ip}",
                    log_type='WEBSOCKET_CONNECTION',
                    user=user_obj,
                    data={
                        'client_ip': client_ip,
                        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                        'connection_type': 'websocket',
                        'timestamp': timezone.now().isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"记录WebSocket连接日志失败: {e}")
            
            logger.info(f"🔌 WebSocket连接: {client_ip} - {user_info}")
        
        return None
    
    def get_client_ip(self, request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 