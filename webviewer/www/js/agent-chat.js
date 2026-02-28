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
    isSending: false,
    streamTimer: null,
    streamText: ''
  };

  // 流式显示的步骤文本
  const STREAM_STEPS = {
    'bydesign': [
      '正在理解你的出行需求...',
      '正在分析出行类型...',
      '正在创建出行记录...',
      '正在保存数据...',
      '完成！✅'
    ],
    'cherry_pick': [
      '正在理解物品信息...',
      '正在分析物品位置...',
      '正在记录物品...',
      '正在保存数据...',
      '完成！✅'
    ],
    'momhand': [
      '正在理解物品信息...',
      '正在分析物品分类...',
      '正在添加物品...',
      '正在保存数据...',
      '完成！✅'
    ]
  };

  /**
   * 初始化聊天组件
   */
  window.initAgentChat = function(config = {}) {
    const chatConfig = { ...DEFAULT_CONFIG, ...config };
    window.chatConfig = chatConfig;
    
    // 加载保存的提示词
    loadSavedPrompt();
    
    // 添加面板悬浮效果和主题色
    enhancePanelStyle();
    
    console.log(`[AgentChat] 已初始化，项目：${chatConfig.project}`);
  };

  /**
   * 获取项目主题色配置
   */
  function getThemeColors() {
    const project = window.chatConfig?.project || 'bydesign';
    
    const themes = {
      'bydesign': {
        // 蓝色主题（已读不回）
        bgGradient: 'linear-gradient(135deg, rgba(219, 234, 254, 0.95) 0%, rgba(191, 219, 254, 0.92) 50%, rgba(224, 242, 254, 0.95) 100%)',
        bgGradientDark: 'linear-gradient(135deg, rgba(219, 234, 254, 0.98) 0%, rgba(191, 219, 254, 0.96) 50%, rgba(224, 242, 254, 0.98) 100%)',
        accentColor: '#3b82f6',
        accentLight: '#dbeafe',
        accentGradient: 'linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(59, 130, 246, 0.04) 100%)',
        borderLeftColor: '#3b82f6'
      },
      'cherry_pick': {
        // 紫色主题（一搬不丢）
        bgGradient: 'linear-gradient(135deg, rgba(243, 232, 255, 0.95) 0%, rgba(233, 213, 255, 0.92) 50%, rgba(245, 243, 255, 0.95) 100%)',
        bgGradientDark: 'linear-gradient(135deg, rgba(243, 232, 255, 0.98) 0%, rgba(233, 213, 255, 0.96) 50%, rgba(245, 243, 255, 0.98) 100%)',
        accentColor: '#a855f7',
        accentLight: '#f3e8ff',
        accentGradient: 'linear-gradient(135deg, rgba(168, 85, 247, 0.12) 0%, rgba(168, 85, 247, 0.04) 100%)',
        borderLeftColor: '#a855f7'
      },
      'momhand': {
        // 绿色主题（妈妈的手）
        bgGradient: 'linear-gradient(135deg, rgba(220, 252, 231, 0.95) 0%, rgba(187, 247, 208, 0.92) 50%, rgba(228, 255, 244, 0.95) 100%)',
        bgGradientDark: 'linear-gradient(135deg, rgba(220, 252, 231, 0.98) 0%, rgba(187, 247, 208, 0.96) 50%, rgba(228, 255, 244, 0.98) 100%)',
        accentColor: '#22c55e',
        accentLight: '#dcfce7',
        accentGradient: 'linear-gradient(135deg, rgba(34, 197, 94, 0.12) 0%, rgba(34, 197, 94, 0.04) 100%)',
        borderLeftColor: '#22c55e'
      }
    };
    
    return themes[project] || themes['bydesign'];
  }

  /**
   * 添加背景虚化层（仅在有 fabPanel 时）
   */
  function addBackdropBlur() {
    // 检查是否有 fabPanel 元素，没有则不添加虚化层
    const panel = document.getElementById('fabPanel');
    if (!panel) return;
    
    // 检查是否已存在虚化层
    if (document.getElementById('chatBackdrop')) return;
    
    const backdrop = document.createElement('div');
    backdrop.id = 'chatBackdrop';
    backdrop.className = 'fixed inset-0 bg-black/20 z-[9998] opacity-0 pointer-events-none transition-opacity duration-300';
    // 只模糊背景，不模糊悬浮窗
    backdrop.style.backdropFilter = 'blur(8px)';
    backdrop.style.webkitBackdropFilter = 'blur(8px)';
    document.body.appendChild(backdrop);
    
    const toggleBtn = document.querySelector('[onclick="togglePanel()"]');
    
    if (panel && toggleBtn) {
      // 确保悬浮窗在虚化层之上
      const glassCard = panel.querySelector('.glass-card');
      if (glassCard) {
        glassCard.style.zIndex = '9999';
        glassCard.style.position = 'relative';
        // 减少玻璃卡片的 backdrop-filter，避免内部内容模糊
        glassCard.style.backdropFilter = 'blur(4px)';
        glassCard.style.webkitBackdropFilter = 'blur(4px)';
      }
      
      // 使用 MutationObserver 监听面板的 hidden 类变化
      const observer = new MutationObserver(() => {
        if (panel.classList.contains('hidden')) {
          // 面板关闭
          backdrop.classList.add('opacity-0', 'pointer-events-none');
          backdrop.classList.remove('pointer-events-auto');
        } else {
          // 面板展开
          backdrop.classList.remove('opacity-0', 'pointer-events-none');
          backdrop.classList.add('pointer-events-auto');
        }
      });
      
      observer.observe(panel, { attributes: true, attributeFilter: ['class'] });
      
      // 点击虚化层关闭面板
      backdrop.addEventListener('click', () => {
        if (typeof togglePanel === 'function') {
          togglePanel();
        }
      });
    }
  }

  /**
   * 增强面板样式（悬浮效果 + 主题色）
   */
  function enhancePanelStyle() {
    const panel = document.getElementById('fabPanel');
    if (!panel) {
      // 没有悬浮窗元素，不执行增强（主页不需要）
      return;
    }
    
    // 找到内部的玻璃卡片并添加悬浮样式类
    const glassCard = panel.querySelector('.glass-card');
    if (glassCard) {
      glassCard.classList.add('chat-panel-enhanced');
    }
    
    // 获取主题色
    const theme = getThemeColors();
    
    // 添加背景虚化层
    addBackdropBlur();
    
    // 添加 CSS 样式
    const style = document.createElement('style');
    style.textContent = `
      .chat-panel-enhanced {
        background: ${theme.bgGradient} !important;
        backdrop-filter: blur(4px) !important;
        -webkit-backdrop-filter: blur(4px) !important;
        box-shadow: 
          0 25px 50px -12px rgba(0, 0, 0, 0.15),
          0 0 0 1px rgba(255, 255, 255, 0.6),
          inset 0 1px 0 rgba(255, 255, 255, 0.8);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
      }
      .chat-panel-enhanced::before {
        content: '';
        position: absolute;
        inset: -1px;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.3) 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        z-index: 10;
      }
      .chat-panel-enhanced:hover {
        background: ${theme.bgGradientDark} !important;
        box-shadow: 
          0 35px 60px -12px rgba(0, 0, 0, 0.2),
          0 0 0 1px rgba(255, 255, 255, 0.7),
          inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transform: translateY(-3px) scale(1.01);
      }
      /* 流式进展样式 */
      .stream-progress {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .stream-step {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 13px;
        transition: all 0.3s ease;
      }
      .stream-step.pending {
        background: rgba(255, 255, 255, 0.5);
        color: #9ca3af;
      }
      .stream-step.active {
        background: ${theme.accentGradient};
        color: ${theme.accentColor};
        font-weight: 500;
      }
      .stream-step.completed {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
      }
      .stream-step .step-icon {
        width: 16px;
        height: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }
      .stream-step.pending .step-icon {
        opacity: 0.3;
      }
      .stream-step.active .step-icon {
        animation: pulse 1.5s infinite;
      }
      @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
      }
      @keyframes typing {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
      .typing-dot {
        animation: typing 1.4s infinite;
        width: 6px;
        height: 6px;
        background: currentColor;
        border-radius: 50%;
        display: inline-block;
      }
      .typing-dot:nth-child(2) { animation-delay: 0.2s; }
      .typing-dot:nth-child(3) { animation-delay: 0.4s; }
      /* 结果消息样式 - 使用主题色系 */
      .chat-panel-enhanced .result-message {
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        border-left: 3px solid;
        background: ${theme.accentGradient};
      }
      .chat-panel-enhanced .result-success {
        border-left-color: ${theme.borderLeftColor};
        background: ${theme.accentGradient};
      }
      .chat-panel-enhanced .result-error {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.10) 0%, rgba(239, 68, 68, 0.04) 100%);
      }
      .chat-panel-enhanced .result-warning {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.10) 0%, rgba(245, 158, 11, 0.04) 100%);
      }
      .chat-panel-enhanced .result-info {
        border-left-color: ${theme.borderLeftColor};
        background: ${theme.accentGradient};
      }
      @keyframes resultSlideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
      }
      .result-message {
        animation: resultSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
    `;
    document.head.appendChild(style);
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
   * 发送消息（仅用于子页面，主页有自己的 sendMessage）
   */
  window.sendMessage = async function() {
    // 检查是否有 fabPanel，没有则说明是主页，不处理
    const panel = document.getElementById('fabPanel');
    if (!panel) return;
    
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
    
    // 显示流式进展
    showStreamProgress();

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
        hideStreamProgress();
        showResult(result.error || '处理失败', 'error');
        updateSendButton(false);
      }
    } catch (error) {
      hideStreamProgress();
      showResult(`发送失败：${error.message}`, 'error');
      updateSendButton(false);
    }
  };

  /**
   * 显示流式进展
   */
  function showStreamProgress() {
    const project = window.chatConfig?.project || 'bydesign';
    const steps = STREAM_STEPS[project] || STREAM_STEPS['bydesign'];
    
    // 获取或创建结果容器
    let resultContainer = document.getElementById('chatResult');
    
    if (!resultContainer) {
      const panel = document.getElementById('fabPanel');
      if (!panel) return;
      
      resultContainer = document.createElement('div');
      resultContainer.id = 'chatResult';
      resultContainer.className = 'mb-4';
      
      const header = panel.querySelector('.border-b');
      if (header && header.parentElement) {
        header.parentElement.insertBefore(resultContainer, header.nextSibling);
      } else {
        panel.insertBefore(resultContainer, panel.firstChild);
      }
    }
    
    // 创建流式进展 HTML
    resultContainer.innerHTML = `
      <div class="stream-progress">
        ${steps.map((step, index) => `
          <div class="stream-step ${index === 0 ? 'active' : 'pending'}" id="stream-step-${index}">
            <span class="step-icon">
              ${index === 0 ? '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>' : '○'}
            </span>
            <span>${step}</span>
          </div>
        `).join('')}
      </div>
    `;
    
    // 流式更新步骤
    let currentStep = 0;
    
    chatState.streamTimer = setInterval(() => {
      if (currentStep < steps.length - 1) {
        // 完成当前步骤
        const currentEl = document.getElementById(`stream-step-${currentStep}`);
        if (currentEl) {
          currentEl.classList.remove('active');
          currentEl.classList.add('completed');
          currentEl.querySelector('.step-icon').innerHTML = '●';
        }
        
        // 激活下一步骤
        currentStep++;
        const nextEl = document.getElementById(`stream-step-${currentStep}`);
        if (nextEl) {
          nextEl.classList.remove('pending');
          nextEl.classList.add('active');
          nextEl.querySelector('.step-icon').innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
        }
      }
    }, 800); // 每 800ms 更新一个步骤
  }

  /**
   * 隐藏流式进展
   */
  function hideStreamProgress() {
    if (chatState.streamTimer) {
      clearInterval(chatState.streamTimer);
      chatState.streamTimer = null;
    }
  }

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
    // 隐藏流式进展
    hideStreamProgress();
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
            hideStreamProgress();
            showResult('处理失败', 'error');
            updateSendButton(false);
            chatState.isSending = false;
          }
        } else if (attempts >= maxAttempts) {
          clearInterval(chatState.pollTimer);
          chatState.polling = false;
          hideStreamProgress();
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
   * 显示结果消息（在面板内）
   */
  function showResult(text, type = 'info') {
    // 获取或创建结果容器（在面板内）
    let resultContainer = document.getElementById('chatResult');
    
    if (!resultContainer) {
      // 在面板内创建结果容器
      const panel = document.getElementById('fabPanel');
      if (!panel) {
        console.log('[AgentChat] 结果:', text);
        return;
      }
      
      resultContainer = document.createElement('div');
      resultContainer.id = 'chatResult';
      resultContainer.className = 'mb-4';
      
      // 插入到面板的开头（标题下方）
      const header = panel.querySelector('.border-b');
      if (header && header.parentElement) {
        header.parentElement.insertBefore(resultContainer, header.nextSibling);
      } else {
        panel.insertBefore(resultContainer, panel.firstChild);
      }
    }
    
    // 只保留最新一条消息（移除旧的）
    resultContainer.innerHTML = '';
    
    // 创建新的结果消息
    const messageEl = document.createElement('div');
    messageEl.className = `result-message result-${type} border rounded-xl px-4 py-3 shadow-sm`;
    
    const icons = {
      'success': '✅',
      'error': '❌',
      'warning': '⚠️',
      'info': 'ℹ️'
    };
    
    messageEl.innerHTML = `
      <div class="flex items-start gap-3">
        <span class="text-lg flex-shrink-0">${icons[type]}</span>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-700 break-words">${text}</p>
        </div>
        <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600 flex-shrink-0 transition-colors p-0.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;
    
    resultContainer.appendChild(messageEl);
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
