 import React from 'react';
import './CommandResultModal.css';

interface CommandResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  command: string;
  result: 'success' | 'error' | 'timeout';
  message: string;
  timestamp: string;
}

const CommandResultModal: React.FC<CommandResultModalProps> = ({
  isOpen,
  onClose,
  command,
  result,
  message,
  timestamp
}) => {
  if (!isOpen) return null;

  const getResultIcon = () => {
    switch (result) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'timeout':
        return '⏰';
      default:
        return '❓';
    }
  };

  const getResultColor = () => {
    switch (result) {
      case 'success':
        return '#10b981';
      case 'error':
        return '#ef4444';
      case 'timeout':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  const getResultTitle = () => {
    switch (result) {
      case 'success':
        return '指令执行成功';
      case 'error':
        return '指令执行失败';
      case 'timeout':
        return '指令执行超时';
      default:
        return '指令执行状态未知';
    }
  };

  const getCommandDisplay = (cmd: string) => {
    const commandMap: { [key: string]: string } = {
      'open_door': '开门',
      'close_door': '关门',
      'start_delivery': '开始配送',
      'stop_robot': '停止机器人'
    };
    return commandMap[cmd] || cmd;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="result-icon" style={{ color: getResultColor() }}>
            {getResultIcon()}
          </div>
          <h2 className="result-title" style={{ color: getResultColor() }}>
            {getResultTitle()}
          </h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div className="command-info">
            <div className="info-row">
              <span className="label">指令类型:</span>
              <span className="value command-type">
                {getCommandDisplay(command)}
              </span>
            </div>
            <div className="info-row">
              <span className="label">执行时间:</span>
              <span className="value timestamp">{timestamp}</span>
            </div>
            <div className="info-row">
              <span className="label">执行结果:</span>
              <span className="value result-message">{message}</span>
            </div>
          </div>

          <div className="result-details">
            {result === 'success' && (
              <div className="success-details">
                <div className="detail-item">
                  <span className="detail-icon">🤖</span>
                  <span>机器人已成功接收并执行指令</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">📡</span>
                  <span>执行结果已反馈到服务器</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">✅</span>
                  <span>系统状态已更新</span>
                </div>
              </div>
            )}

            {result === 'error' && (
              <div className="error-details">
                <div className="detail-item">
                  <span className="detail-icon">⚠️</span>
                  <span>指令执行过程中出现错误</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">🔧</span>
                  <span>请检查机器人状态和连接</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">📞</span>
                  <span>如问题持续，请联系技术支持</span>
                </div>
              </div>
            )}

            {result === 'timeout' && (
              <div className="timeout-details">
                <div className="detail-item">
                  <span className="detail-icon">⏰</span>
                  <span>指令执行超时</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">🔄</span>
                  <span>请稍后重试或检查机器人状态</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">📊</span>
                  <span>可通过状态面板查看最新状态</span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button className="primary-button" onClick={onClose}>
            确定
          </button>
          {result === 'error' && (
            <button className="secondary-button" onClick={onClose}>
              重试
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommandResultModal; 