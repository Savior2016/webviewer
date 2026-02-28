/**
 * Agent Chat - 统一的聊天组件
 * 用于 By Design / Cherry Pick / Momhand 三个项目
 * 
 * 配置对象 (window.chatConfig):
 * - project: 项目名称 (bydesign/cherry_pick/momhand)
 * - colors: 颜色配置
 * - defaultPrompt: 默认提示词
 */

(function() {
  // 默认配置
  const DEFAULT_CONFIG = {
    project: 'bydesign',
    colors: {
      primary: 'from-blue-500 to-cyan-500',
      primaryBg: 'bg-blue-50',
      primaryText: 'text-blue-600',
      gradient: 'linear-gradient(135deg, #1e3a5f 0%, #0f4c75 50%, #1b5e8b 100%)'
    },
    defaultPrompt: ''
  };

  // 状态
  let chatState = {
    polling: false,
    currentMsgId: null,
    pollTimer: null,
    isSending: false
  };

  /**
   * 初始化聊天组件
   */
  window.initAgentChat = function(config = {}) {
    const chatConfig = { ...DEFAULT_CONFIG, ...config };
    window.chatConfig = chatConfig;
    
    // 加载保存的提示词
    loadSavedPrompt();
    
    // 添加面板悬浮效果
    enhancePanelStyle();
    
    console.log(`[AgentChat] 已初始化，项目：${chatConfig.project}`);
  };

  /**
   * 增强面板样式（悬浮效果）
   */
  function enhancePanelStyle() {
    const panel = document.getElementById('fabPanel');
    if (panel) {
      // 添加更强的阴影和边框
      panel.classList.add('shadow-2xl', 'border', 'border-white/30');
      
      // 添加 CSS 动画效果
      const style = document.createElement('style');
      style.textContent = `
        #fabPanel {
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        #fabPanel:hover {
          box-shadow: 0 35px 60px -12px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.2);
          transform: translateY(-2px);
        }
        .chat-toast {
          backdrop-filter: blur(12px);
          box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.15);
        }
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-20px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        .toast-animate {
          animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
      `;
      document.head.appendChild(style);
    }
  }

  /**
   * 加载保存的提示词
   */
  function loadSavedPrompt() {
    const project = window.chatConfig?.project || 'bydesign';
    const savedPrompt = localStorage.getItem(`${project}_systemPrompt`);
    const defaultPrompt = window.chatConfig?.defaultPrompt || '';
    
    const promptEl = document.getElementById('systemPrompt');
    if (promptEl) {
      promptEl.value = savedPrompt || defaultPrompt;
    }
  }

  /**
   * 填充示例文本
   */
  window.fillExample = function(text) {
    const input = document.getElementById('messageInput');
    if (input) {
      input.value = text;
      input.focus();
    }
  };

  /**
   * 发送消息
   */
  window.sendMessage = async function() {
    if (chatState.isSending) return;
    
    const input = document.getElementById('messageInput');
    const message = input?.value.trim();
    
    if (!message) {
      showResult('请输入内容', 'warning');
      return;
    }

    // 设置发送中状态
    chatState.isSending = true;
    updateSendButton(true);
    input.value = '';

    try {
      const response = await fetch('/api/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, timestamp: Date.now() })
      });
      const result = await response.json();

      if (result.success) {
        const msgId = result.msg_id;
        if (result.processing) {
          // 异步处理，开始轮询
          pollResult(msgId);
        } else {
          // 同步处理完成
          handleResult(result);
        }
      } else {
        showResult(result.error || '处理失败', 'error');
        updateSendButton(false);
      }
    } catch (error) {
      showResult(`发送失败：${error.message}`, 'error');
      updateSendButton(false);
    }
  };

  /**
   * 更新发送按钮状态
   */
  function updateSendButton(isSending) {
    const sendBtn = document.querySelector('button[onclick="sendMessage()"]');
    if (!sendBtn) return;
    
    if (isSending) {
      sendBtn.disabled = true;
      sendBtn.classList.add('opacity-70', 'cursor-wait');
      sendBtn.innerHTML = `
        <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>发送中...</span>
      `;
    } else {
      sendBtn.disabled = false;
      sendBtn.classList.remove('opacity-70', 'cursor-wait');
      sendBtn.innerHTML = `
        <span>📤</span>
        <span>发送</span>
      `;
    }
  }

  /**
   * 处理结果
   */
  function handleResult(result) {
    updateSendButton(false);
    chatState.isSending = false;
    
    const message = result.message || '处理完成';
    
    if (result.data?.success === false) {
      showResult(message, 'error');
    } else {
      showResult(message, 'success');
      
      if (result.refresh) {
        setTimeout(() => {
          window.location.href = result.refresh + '?t=' + Date.now();
        }, 1500);
      } else {
        // 刷新当前页面数据
        refreshCurrentPage();
      }
    }
  }

  /**
   * 轮询结果
   */
  function pollResult(msgId) {
    if (chatState.polling) return;
    
    chatState.polling = true;
    chatState.currentMsgId = msgId;
    
    let attempts = 0;
    const maxAttempts = 60;
    
    chatState.pollTimer = setInterval(async () => {
      attempts++;
      
      try {
        const response = await fetch(`/api/message-result?msg_id=${msgId}`);
        const result = await response.json();
        
        if (result.processed || !result.success) {
          clearInterval(chatState.pollTimer);
          chatState.polling = false;
          
          if (result.data) {
            handleResult(result.data);
          } else {
            showResult('处理失败', 'error');
            updateSendButton(false);
            chatState.isSending = false;
          }
        } else if (attempts >= maxAttempts) {
          clearInterval(chatState.pollTimer);
          chatState.polling = false;
          showResult('处理超时，请刷新页面查看结果', 'warning');
          updateSendButton(false);
          chatState.isSending = false;
        }
      } catch (error) {
        console.error('轮询失败:', error);
      }
    }, 500);
  }

  /**
   * 显示结果消息（顶部 Toast）
   */
  function showResult(text, type = 'info') {
    // 创建或获取 toast 容器
    let toastContainer = document.getElementById('chatToastContainer');
    
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'chatToastContainer';
      toastContainer.className = 'fixed top-4 left-0 right-0 z-[200] flex justify-center pointer-events-none px-4';
      document.body.appendChild(toastContainer);
    }
    
    const colors = {
      'success': 'bg-green-500/95 border-green-400 text-white',
      'error': 'bg-red-500/95 border-red-400 text-white',
      'warning': 'bg-amber-500/95 border-amber-400 text-white',
      'info': 'bg-blue-500/95 border-blue-400 text-white'
    };

    const icons = {
      'success': '✅',
      'error': '❌',
      'warning': '⚠️',
      'info': 'ℹ️'
    };

    // 移除旧的 toast（只保留最新一条）
    toastContainer.innerHTML = '';
    
    // 创建新的 toast
    const toast = document.createElement('div');
    toast.className = `chat-toast ${colors[type]} border px-5 py-3.5 rounded-2xl shadow-lg toast-animate pointer-events-auto max-w-md w-full`;
    toast.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="text-xl flex-shrink-0">${icons[type]}</span>
        <span class="flex-1 font-medium text-sm">${text}</span>
        <button onclick="this.parentElement.parentElement.remove()" class="text-white/70 hover:text-white flex-shrink-0 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;
    
    toastContainer.appendChild(toast);

    // 5 秒后自动移除
    setTimeout(() => {
      if (toast.parentElement) {
        toast.style.transition = 'all 0.3s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => toast.remove(), 300);
      }
    }, 5000);
  }

  /**
   * 刷新当前页面数据
   */
  function refreshCurrentPage() {
    const project = window.chatConfig?.project || 'bydesign';
    
    // 根据项目调用不同的刷新函数
    const refreshFunctions = {
      'bydesign': () => {
        if (typeof loadTrips === 'function') loadTrips();
        if (typeof loadChecklist === 'function') loadChecklist();
        if (typeof loadTemplatesPreview === 'function') loadTemplatesPreview();
      },
      'cherry_pick': () => {
        if (typeof loadMoves === 'function') loadMoves();
        if (typeof loadItems === 'function') loadItems();
      },
      'momhand': () => {
        if (typeof loadItems === 'function') loadItems();
        if (typeof loadStats === 'function') loadStats();
      }
    };

    const refresh = refreshFunctions[project];
    if (refresh) {
      refresh();
    }
  }

  /**
   * 显示设置弹窗
   */
  window.showSettings = function() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
      modal.classList.remove('hidden');
      loadSavedPrompt();
    }
  };

  /**
   * 隐藏设置弹窗
   */
  window.hideSettings = function() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
      modal.classList.add('hidden');
    }
  };

  /**
   * 保存设置
   */
  window.saveSettings = async function() {
    const promptEl = document.getElementById('systemPrompt');
    const prompt = promptEl?.value || '';
    const project = window.chatConfig?.project || 'bydesign';

    try {
      // 保存到后端
      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ system_prompt: prompt })
      });
      const result = await response.json();

      if (result.success) {
        // 同时保存到 localStorage
        localStorage.setItem(`${project}_systemPrompt`, prompt);
        showResult('设置已保存', 'success');
        hideSettings();
      } else {
        showResult('保存失败：' + (result.error || '未知错误'), 'error');
      }
    } catch (error) {
      // 降级：只保存到 localStorage
      localStorage.setItem(`${project}_systemPrompt`, prompt);
      showResult('设置已保存（本地）', 'success');
      hideSettings();
    }
  };

  /**
   * 恢复默认提示词
   */
  window.resetPrompt = function() {
    if (confirm('确定要恢复默认提示词吗？')) {
      const promptEl = document.getElementById('systemPrompt');
      if (promptEl && window.chatConfig?.defaultPrompt) {
        promptEl.value = window.chatConfig.defaultPrompt;
      }
    }
  };

  /**
   * 设置弹窗点击外部关闭
   */
  window.initSettingsModal = function() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
      modal.addEventListener('click', function(e) {
        if (e.target === this) {
          hideSettings();
        }
      });
    }
  };

  // 自动初始化设置模态框
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initSettingsModal);
  } else {
    window.initSettingsModal();
  }
})();
