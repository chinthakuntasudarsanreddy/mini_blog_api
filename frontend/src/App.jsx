import { useEffect, useRef, useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const chatBodyRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      loadChatHistory();
    }
  }, [isOpen]);

  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop =
        chatBodyRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const loadChatHistory = async () => {
    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        return;
      }

      const response = await axios.get(
        `${API_URL}/api/ai-support/history`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const history = [];

      response.data.forEach((chat) => {
        history.push({
          id: `${chat.id}-question`,
          type: "user",
          text: chat.question,
        });

        history.push({
          id: `${chat.id}-answer`,
          type: "ai",
          text: chat.ai_response,
        });
      });

      setMessages(history);
    } catch (error) {
      console.error(
        "Could not load AI support history:",
        error
      );
    }
  };

  const sendMessage = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    const userMessage = {
      id: `user-${Date.now()}`,
      type: "user",
      text: trimmedMessage,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setMessage("");
    setLoading(true);

    try {
      const token = localStorage.getItem("access_token");

      const response = await axios.post(
        `${API_URL}/api/ai-support/`,
        {
          message: trimmedMessage,
        },
        {
          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : {},
        }
      );

      const aiMessage = {
        id: `ai-${Date.now()}`,
        type: "ai",
        text: response.data.ai_response,
      };

      setMessages((previous) => [
        ...previous,
        aiMessage,
      ]);
    } catch (error) {
      console.error(
        "AI Support request failed:",
        error
      );

      let errorText =
        "Sorry, something went wrong. Please try again.";

      if (error.response?.status === 401) {
        errorText =
          "Please log in to use AI Support.";
      }

      const errorMessage = {
        id: `error-${Date.now()}`,
        type: "ai",
        text: errorText,
      };

      setMessages((previous) => [
        ...previous,
        errorMessage,
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const askSuggestion = (question) => {
    setMessage(question);
  };

  return (
    <div className="app">

      <div className="demo-content">
        <h1>Mini Blog Platform</h1>

        <p>
          Welcome to your blog platform.
        </p>

        <p>
          Need help? Click the support button in the
          bottom-right corner.
        </p>
      </div>

      {isOpen && (
        <div className="support-chat">

          <div className="chat-header">

            <div className="chat-title">

              <div className="bot-avatar">
                🤖
              </div>

              <div>
                <h2>AI Support</h2>
                <span>● Online</span>
              </div>

            </div>

            <button
              className="close-button"
              onClick={() => setIsOpen(false)}
              aria-label="Close AI Support"
            >
              ×
            </button>

          </div>

          <div
            className="chat-body"
            ref={chatBodyRef}
          >

            {messages.length === 0 && (

              <div className="welcome-message">

                <div className="welcome-icon">
                  🤖
                </div>

                <h3>
                  Hi! How can I help?
                </h3>

                <p>
                  Ask me anything about your blog platform.
                </p>

                <div className="suggestions">

                  <button
                    onClick={() =>
                      askSuggestion(
                        "How do I create a post?"
                      )
                    }
                  >
                    How do I create a post?
                  </button>

                  <button
                    onClick={() =>
                      askSuggestion(
                        "How does the Premium plan work?"
                      )
                    }
                  >
                    How do subscriptions work?
                  </button>

                  <button
                    onClick={() =>
                      askSuggestion(
                        "Where can I see my billing history?"
                      )
                    }
                  >
                    Billing help
                  </button>

                  <button
                    onClick={() =>
                      askSuggestion(
                        "What does dashboard analytics mean?"
                      )
                    }
                  >
                    Dashboard analytics
                  </button>

                </div>

              </div>

            )}

            {messages.map((item) => (

              <div
                key={item.id}
                className={`message-row ${item.type}`}
              >

                {item.type === "ai" && (
                  <div className="small-avatar">
                    🤖
                  </div>
                )}

                <div className="message-bubble">
                  {item.text}
                </div>

              </div>

            ))}

            {loading && (

              <div className="message-row ai">

                <div className="small-avatar">
                  🤖
                </div>

                <div className="message-bubble typing">

                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              </div>

            )}

          </div>

          <div className="chat-input-area">

            <textarea
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask something..."
              rows="1"
              disabled={loading}
            />

            <button
              className="send-button"
              onClick={sendMessage}
              disabled={!message.trim() || loading}
              aria-label="Send message"
            >
              ➤
            </button>

          </div>

          <div className="chat-footer">
            AI Support Assistant
          </div>

        </div>
      )}

      <button
        className={`support-button ${
          isOpen ? "opened" : ""
        }`}
        onClick={() =>
          setIsOpen((previous) => !previous)
        }
        aria-label="Open AI Support"
      >
        {isOpen ? "×" : "💬"}
      </button>

    </div>
  );
}

export default App;