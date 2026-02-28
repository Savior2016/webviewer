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
    pollTimer: null
  };

  /**
   * 初始化聊天组件
   */
  window.initAgentChat = function(config = {}) {
    const chatConfig = { ...DEFAULT_CONFIG, ...config };
    window.chatConfig = chatConfig;
    
    // 加载保存的提示词
    loadSavedPrompt();
    
    console.log(`[AgentChat] 已初始化，项目：${chatConfig.project}`);
  };

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
    const input = document.getElementById('messageInput');
    const message = input?.value.trim();
    
    if (!message) {
      showResult('请输入内容', 'warning');
      return;
    }

    // 显示 loading 状态
    showLoading(true);
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
        showLoading(false);
      }
    } catch (error) {
      showResult(`发送失败：${error.message}`, 'error');
      showLoading(false);
    }
  };

  /**
   * 处理结果
   */
  function handleResult(result) {
    showLoading(false);
    
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
            showLoading(false);
          }
        } else if (attempts >= maxAttempts) {
          clearInterval(chatState.pollTimer);
          chatState.polling = false;
          showResult('处理超时，请刷新页面查看结果', 'warning');
          showLoading(false);
        }
      } catch (error) {
        console.error('轮询失败:', error);
      }
    }, 500);
  }

  /**
   * 显示 loading 状态
   */
  function showLoading(isLoading) {
    const loadingEl = document.getElementById('chatLoading');
    const sendBtn = document.querySelector('button[onclick="sendMessage()"]');
    
    if (loadingEl) {
      if (isLoading) {
        loadingEl.classList.remove('hidden');
        loadingEl.innerHTML = `
          <div class="flex items-center justify-center gap-2 text-sm">
            <div class="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent"></div>
            <span>正在处理中...</span>
          </div>
        `;
      } else {
        loadingEl.classList.add('hidden');
      }
    }
    
    if (sendBtn) {
      sendBtn.disabled = isLoading;
      if (isLoading) {
        sendBtn.classList.add('opacity-50', 'cursor-not-allowed');
      } else {
        sendBtn.classList.remove('opacity-50', 'cursor-not-allowed');
      }
    }
  }

  /**
   * 显示结果消息
   */
  function showResult(text, type = 'info') {
    const resultEl = document.getElementById('chatResult');
    
    if (!resultEl) {
      console.log('[AgentChat] 结果:', text);
      return;
    }

    const colors = {
      'success': 'bg-green-50 border-green-200 text-green-700',
      'error': 'bg-red-50 border-red-200 text-red-700',
      'warning': 'bg-amber-50 border-amber-200 text-amber-700',
      'info': 'bg-blue-50 border-blue-200 text-blue-700'
    };

    const icons = {
      'success': '✅',
      'error': '❌',
      'warning': '⚠️',
      'info': 'ℹ️'
    };

    resultEl.className = `${colors[type]} border px-4 py-3 rounded-xl shadow-lg expand-in text-sm`;
    resultEl.innerHTML = `
      <div class="flex items-start gap-2">
        <span class="text-lg flex-shrink-0">${icons[type]}</span>
        <span class="flex-1">${text}</span>
        <button onclick="this.parentElement.parentElement.classList.add('hidden')" class="text-current opacity-50 hover:opacity-100 flex-shrink-0">×</button>
      </div>
    `;
    resultEl.classList.remove('hidden');

    // 5 秒后自动隐藏
    setTimeout(() => {
      resultEl.classList.add('hidden');
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
