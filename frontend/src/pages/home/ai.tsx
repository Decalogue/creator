import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Avatar,
  Spin,
  Select,
  message,
  Empty,
  Divider,
} from 'antd';
import {
  SendOutlined,
  UserOutlined,
  RobotOutlined,
  ClearOutlined,
  CopyOutlined,
  CheckOutlined,
  MenuOutlined,
  CloseOutlined,
} from '@ant-design/icons';
import MarkdownIt from 'markdown-it';
import axios from 'axios';

// 类型声明（Umi define 注入的全局变量）
declare const API_URL: string;

const { TextArea } = Input;
const { Text, Paragraph } = Typography;
const { Option } = Select;

// 初始化 Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true,
});

// API 配置
const API_BASE_URL = API_URL;

// 常量定义
const STREAM_UPDATE_THROTTLE = 50; // 流式更新节流时间（毫秒）
const MAX_MESSAGE_HISTORY = 20; // 前端保留的最大消息数

// 消息类型定义
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  model?: string;
  streaming?: boolean;
}

// 模型类型
type ModelType = 'gemini-3-pro' | 'gemini-3-flash' | 'deepseek-v3-2';

// 获取模型显示名称
const getModelDisplayName = (model: ModelType | string): string => {
  const modelMap: Record<string, string> = {
    'gemini-3-pro': 'Gemini 3 Pro',
    'gemini-3-flash': 'Gemini 3 Flash',
    'deepseek-v3-2': 'DeepSeek V3.2',
  };
  return modelMap[model] || model || 'Unknown';
};

// 获取模型对应的头像路径
const getModelAvatar = (model: ModelType | string | undefined): string => {
  if (!model) return '/avatars/assistant.png';
  
  if (model === 'deepseek-v3-2') {
    return '/avatars/deepseek.png';
  } else if (model === 'gemini-3-pro' || model === 'gemini-3-flash') {
    return '/avatars/google.png';
  }
  
  return '/avatars/assistant.png';
};

// 获取用户头像路径
const getUserAvatar = (): string => {
  return '/avatars/user.png';
};

// 消息内容组件（优化 Markdown 渲染）
const MessageContent: React.FC<{ message: Message }> = React.memo(({ message }) => {
  const htmlContent = React.useMemo(() => md.render(message.content || ''), [message.content]);
  
  return (
    <>
      <div
        className="markdown-content"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
        style={{
          lineHeight: '1.8',
          wordBreak: 'break-word',
        }}
      />
      {message.streaming && (
        <Spin size="small" style={{ marginLeft: '8px', display: 'inline-block' }} />
      )}
    </>
  );
});

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<ModelType>('deepseek-v3-2');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [sidebarVisible, setSidebarVisible] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<any>(null);
  const streamUpdateTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastStreamUpdateRef = useRef<number>(0);

  // 自动滚动到底部（节流优化）
  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // 发送消息后自动聚焦输入框
  useEffect(() => {
    if (!loading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading]);

  // 复制消息内容
  const handleCopy = useCallback(async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedId(messageId);
      message.success('已复制到剪贴板');
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      message.error('复制失败');
    }
  }, []);

  // 清空对话
  const handleClear = useCallback(() => {
    setMessages([]);
    setInputValue('');
    message.info('对话已清空');
    if (streamUpdateTimerRef.current) {
      clearTimeout(streamUpdateTimerRef.current);
      streamUpdateTimerRef.current = null;
    }
  }, []);

  // 节流更新流式消息内容
  const throttledUpdateStreamMessage = useCallback((messageId: string, content: string) => {
    const now = Date.now();
    
    if (now - lastStreamUpdateRef.current < STREAM_UPDATE_THROTTLE) {
      if (streamUpdateTimerRef.current) {
        clearTimeout(streamUpdateTimerRef.current);
      }
      streamUpdateTimerRef.current = setTimeout(() => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === messageId
              ? { ...msg, content, streaming: true }
              : msg
          )
        );
        lastStreamUpdateRef.current = Date.now();
        scrollToBottom();
      }, STREAM_UPDATE_THROTTLE);
    } else {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId
            ? { ...msg, content, streaming: true }
            : msg
        )
      );
      lastStreamUpdateRef.current = now;
      scrollToBottom();
    }
  }, [scrollToBottom]);

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}-${Math.random()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => {
      const newMessages = [...prev, userMessage];
      return newMessages.slice(-MAX_MESSAGE_HISTORY);
    });
    setInputValue('');
    setLoading(true);

    const assistantMessageId = `assistant-${Date.now()}-${Math.random()}`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      model: selectedModel,
      streaming: true,
    };

    setMessages((prev) => [...prev, assistantMessage]);

    try {
      // 先尝试流式请求
      try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: [
              ...messages.map((msg) => ({
                role: msg.role,
                content: msg.content,
              })),
              {
                role: 'user',
                content: userMessage.content,
              },
            ],
            model: selectedModel,
            stream: true,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          throw new Error('流式请求返回 JSON，使用常规请求');
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('无法读取流式响应');
        }

        const decoder = new TextDecoder();
        let fullContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          if (chunk) {
            fullContent += chunk;
            throttledUpdateStreamMessage(assistantMessageId, fullContent);
          }
        }

        if (streamUpdateTimerRef.current) {
          clearTimeout(streamUpdateTimerRef.current);
          streamUpdateTimerRef.current = null;
        }

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, content: fullContent, streaming: false }
              : msg
          )
        );
        setLoading(false);
        scrollToBottom();
        return;
      } catch (streamError) {
        console.log('流式请求失败，使用常规请求:', streamError);
      }

      // 使用常规请求（非流式）
      const messagesToSend = [
        ...messages.map((msg) => ({
          role: msg.role,
          content: msg.content,
        })),
        {
          role: 'user',
          content: userMessage.content,
        },
      ];

      const fallbackResponse = await axios.post(`${API_BASE_URL}/api/chat`, {
        messages: messagesToSend,
        model: selectedModel,
        stream: false,
      });

      const responseData = fallbackResponse.data;
      let responseContent = '';
      
      if (responseData.code === 0 && responseData.content) {
        responseContent = responseData.content;
      } else if (responseData.content) {
        responseContent = responseData.content;
      } else if (responseData.message) {
        responseContent = responseData.message;
      } else {
        responseContent = '抱歉，发生了错误';
      }

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: responseContent,
                streaming: false,
              }
            : msg
        )
      );
      scrollToBottom();
    } catch (error: any) {
      console.error('Error sending message:', error);
      
      if (streamUpdateTimerRef.current) {
        clearTimeout(streamUpdateTimerRef.current);
        streamUpdateTimerRef.current = null;
      }
      
      let errorMessage = '抱歉，无法连接到 AI 服务。请检查网络连接或稍后重试。';
      
      if (error.response) {
        const status = error.response.status;
        if (status === 400) {
          errorMessage = '请求格式错误，请重试';
        } else if (status === 500) {
          errorMessage = '服务器内部错误，请稍后重试';
        } else if (status >= 500) {
          errorMessage = '服务器错误，请稍后重试';
        }
      } else if (error.request) {
        errorMessage = '网络连接失败，请检查网络设置';
      }
      
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: errorMessage,
                streaming: false,
              }
            : msg
        )
      );
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // 处理键盘事件
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 优化：使用 useMemo 缓存模型显示名称
  const modelDisplayName = useMemo(() => getModelDisplayName(selectedModel), [selectedModel]);

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: '***REMOVED***ffffff',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      }}
    >
      {/* 顶部导航栏 - 专业简洁风格 */}
      <div
        style={{
          height: '64px',
          borderBottom: '1px solid ***REMOVED***e5e7eb',
          background: '***REMOVED***ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={() => setSidebarVisible(!sidebarVisible)}
            style={{ fontSize: '16px' }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Avatar
              src={getModelAvatar(selectedModel)}
              icon={<RobotOutlined />}
              shape="circle"
              size={32}
              className="model-avatar"
              onError={() => false}
            />
            <div>
              <Text strong style={{ fontSize: '16px', color: '***REMOVED***111827' }}>
                AI 助手
              </Text>
              <div style={{ fontSize: '12px', color: '***REMOVED***6b7280', lineHeight: '1.2' }}>
                {modelDisplayName}
              </div>
            </div>
          </div>
        </div>
        
        <Space size="middle">
          <Select
            value={selectedModel}
            onChange={setSelectedModel}
            style={{ width: 160 }}
            size="middle"
            bordered={false}
          >
            <Option value="deepseek-v3-2">DeepSeek V3.2</Option>
            <Option value="gemini-3-flash">Gemini 3 Flash</Option>
            <Option value="gemini-3-pro">Gemini 3 Pro</Option>
          </Select>
          <Button
            type="text"
            icon={<ClearOutlined />}
            onClick={handleClear}
            disabled={messages.length === 0}
            style={{ color: '***REMOVED***6b7280' }}
          >
            清空对话
          </Button>
        </Space>
      </div>

      {/* 主内容区域 */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* 侧边栏（可选，类似 Claude） */}
        {sidebarVisible && (
          <div
            style={{
              width: '280px',
              borderRight: '1px solid ***REMOVED***e5e7eb',
              background: '***REMOVED***f9fafb',
              padding: '16px',
              overflowY: 'auto',
            }}
          >
            <div style={{ marginBottom: '16px' }}>
              <Text strong style={{ fontSize: '14px', color: '***REMOVED***111827' }}>
                对话历史
              </Text>
            </div>
            <Empty
              description={
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  暂无历史对话
                </Text>
              }
              style={{ marginTop: '40px' }}
            />
          </div>
        )}

        {/* 聊天区域 */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            background: '***REMOVED***ffffff',
          }}
        >
          {/* 消息列表 */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '24px',
              background: '***REMOVED***ffffff',
            }}
          >
            {messages.length === 0 ? (
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                  marginTop: '-100px',
                }}
              >
                <Avatar
                  src={getModelAvatar(selectedModel)}
                  icon={<RobotOutlined />}
                  shape="circle"
                  size={64}
                  className="model-avatar"
                  style={{ marginBottom: '24px' }}
                  onError={() => false}
                />
                <Text
                  style={{
                    fontSize: '20px',
                    fontWeight: 500,
                    color: '***REMOVED***111827',
                    marginBottom: '8px',
                  }}
                >
                  开始对话
                </Text>
                <Text
                  type="secondary"
                  style={{
                    fontSize: '14px',
                    color: '***REMOVED***6b7280',
                    textAlign: 'center',
                    maxWidth: '400px',
                  }}
                >
                  支持 Gemini 3 Pro、Gemini 3 Flash 和 DeepSeek V3.2
                </Text>
              </div>
            ) : (
              <div style={{ maxWidth: '768px', margin: '0 auto' }}>
                {messages.map((msg, index) => (
                  <div
                    key={msg.id}
                    style={{
                      marginBottom: index === messages.length - 1 ? 0 : '32px',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        gap: '16px',
                        alignItems: 'flex-start',
                        flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                        justifyContent: msg.role === 'user' ? 'flex-start' : 'flex-start',
                      }}
                    >
                      <Avatar
                        src={
                          msg.role === 'user'
                            ? getUserAvatar()
                            : getModelAvatar(msg.model)
                        }
                        icon={
                          msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />
                        }
                        shape="circle"
                        size={32}
                        style={{
                          backgroundColor:
                            msg.role === 'user' ? '***REMOVED***95EC69' : 'transparent',
                          flexShrink: 0,
                        }}
                        className={msg.role === 'assistant' ? 'model-avatar' : ''}
                        onError={() => false}
                      />
                      <div
                        style={{
                          maxWidth: msg.role === 'user' ? '70%' : '100%',
                          minWidth: msg.role === 'user' ? '120px' : 'auto',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        }}
                      >
                        <div
                          style={{
                            padding: '16px 20px',
                            borderRadius: '12px',
                            background:
                              msg.role === 'user' ? '***REMOVED***95EC69' : '***REMOVED***f3f4f6',
                            color: msg.role === 'user' ? '***REMOVED***000000' : '***REMOVED***111827',
                            lineHeight: '1.8',
                            wordBreak: 'break-word',
                            display: 'inline-block',
                            maxWidth: '100%',
                          }}
                        >
                          {msg.role === 'user' ? (
                            <Paragraph
                              style={{
                                margin: 0,
                                whiteSpace: 'pre-wrap',
                                color: '***REMOVED***000000',
                                fontSize: '16px',
                                lineHeight: '1.8',
                              }}
                            >
                              {msg.content}
                            </Paragraph>
                          ) : (
                            <MessageContent message={msg} />
                          )}
                        </div>
                        {msg.role === 'assistant' && msg.content && (
                          <div
                            style={{
                              marginTop: '8px',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '12px',
                              alignSelf: 'flex-start',
                            }}
                          >
                            <Button
                              type="text"
                              size="small"
                              icon={
                                copiedId === msg.id ? (
                                  <CheckOutlined />
                                ) : (
                                  <CopyOutlined />
                                )
                              }
                              onClick={() => handleCopy(msg.content, msg.id)}
                              style={{
                                color: '***REMOVED***6b7280',
                                fontSize: '12px',
                                height: '24px',
                                padding: '0 8px',
                              }}
                            >
                              {copiedId === msg.id ? '已复制' : '复制'}
                            </Button>
                            {msg.model && (
                              <Text
                                type="secondary"
                                style={{
                                  fontSize: '11px',
                                  color: '***REMOVED***9ca3af',
                                }}
                              >
                                {getModelDisplayName(msg.model)}
                              </Text>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* 输入区域 - 专业简洁风格 */}
          <div
            style={{
              borderTop: '1px solid ***REMOVED***e5e7eb',
              background: '***REMOVED***ffffff',
              padding: '16px 24px',
            }}
          >
            <div
              style={{
                maxWidth: '768px',
                margin: '0 auto',
                display: 'flex',
                gap: '12px',
                alignItems: 'flex-end',
              }}
            >
              <div style={{ flex: 1 }}>
                <TextArea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="输入消息..."
                  autoSize={{ minRows: 1, maxRows: 6 }}
                  disabled={loading}
                  bordered={false}
                  style={{
                    background: '***REMOVED***f9fafb',
                    borderRadius: '12px',
                    padding: '12px 16px',
                    resize: 'none',
                    fontSize: '14px',
                    lineHeight: '1.6',
                  }}
                />
                <div
                  style={{
                    marginTop: '8px',
                    fontSize: '12px',
                    color: '***REMOVED***9ca3af',
                    textAlign: 'right',
                  }}
                >
                  {loading ? 'AI 正在思考...' : 'Shift + Enter 换行，Enter 发送'}
                </div>
              </div>
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={loading}
                disabled={!inputValue.trim()}
                size="large"
                style={{
                  height: '40px',
                  width: '40px',
                  padding: 0,
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <style>{`
        /* 头像样式：去除背景，确保圆形显示 */
        .ant-avatar.model-avatar {
          background: transparent !important;
          overflow: hidden;
          border: none;
        }
        .ant-avatar.model-avatar > img {
          object-fit: cover;
          width: 100%;
          height: 100%;
          background: transparent !important;
          border-radius: 50%;
          mix-blend-mode: multiply;
        }
        
        /* Markdown 内容样式 - 专业简洁 */
        .markdown-content {
          color: inherit;
          font-size: 16px;
        }
        .markdown-content h1,
        .markdown-content h2,
        .markdown-content h3,
        .markdown-content h4 {
          margin-top: 20px;
          margin-bottom: 12px;
          font-weight: 600;
          color: inherit;
        }
        .markdown-content h1 {
          font-size: 1.5em;
        }
        .markdown-content h2 {
          font-size: 1.3em;
        }
        .markdown-content h3 {
          font-size: 1.1em;
        }
        .markdown-content p {
          margin: 12px 0;
          line-height: 1.8;
        }
        .markdown-content code {
          background: rgba(0, 0, 0, 0.06);
          padding: 2px 6px;
          border-radius: 4px;
          font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
          font-size: 0.9em;
          color: inherit;
        }
        .markdown-content pre {
          background: rgba(0, 0, 0, 0.04);
          padding: 16px;
          border-radius: 8px;
          overflow-x: auto;
          margin: 16px 0;
          border: 1px solid rgba(0, 0, 0, 0.06);
        }
        .markdown-content pre code {
          background: none;
          padding: 0;
        }
        .markdown-content ul,
        .markdown-content ol {
          margin: 12px 0;
          padding-left: 24px;
        }
        .markdown-content li {
          margin: 6px 0;
          line-height: 1.8;
        }
        .markdown-content a {
          color: ***REMOVED***2563eb;
          text-decoration: none;
        }
        .markdown-content a:hover {
          text-decoration: underline;
        }
        .markdown-content blockquote {
          border-left: 3px solid ***REMOVED***e5e7eb;
          padding-left: 16px;
          margin: 16px 0;
          color: ***REMOVED***6b7280;
          font-style: italic;
        }
        .markdown-content table {
          border-collapse: collapse;
          width: 100%;
          margin: 16px 0;
          font-size: 0.9em;
        }
        .markdown-content th,
        .markdown-content td {
          border: 1px solid ***REMOVED***e5e7eb;
          padding: 10px 12px;
          text-align: left;
        }
        .markdown-content th {
          background: ***REMOVED***f9fafb;
          font-weight: 600;
        }
        .markdown-content hr {
          border: none;
          border-top: 1px solid ***REMOVED***e5e7eb;
          margin: 24px 0;
        }
      `}</style>
    </div>
  );
};

export default AIAssistant;
