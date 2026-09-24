
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "../ai-support.css";

const API_URL = "http://127.0.0.1:8000";

function AISupport() {
    const [isOpen, setIsOpen] = useState(false);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    const [messages, setMessages] = useState([
        {
            type: "ai",
            text: "Hi! How can I help? Ask me anything about your blog platform."
        }
    ]);

    const messagesRef = useRef(null);

    useEffect(() => {
        if (messagesRef.current) {
            messagesRef.current.scrollTop =
                messagesRef.current.scrollHeight;
        }
    }, [messages, loading]);

    const sendMessage = async (question = message) => {
        const text = question.trim();

        if (!text || loading) {
            return;
        }

        // Add user message
        setMessages((oldMessages) => [
            ...oldMessages,
            {
                type: "user",
                text: text
            }
        ]);

        setMessage("");
        setLoading(true);

        try {
            const token = localStorage.getItem("access_token");

            const response = await axios.post(
                `${API_URL}/api/ai-support/`,
                {
                    message: text
                },
                {
                    headers: token
                        ? {
                              Authorization: `Bearer ${token}`
                          }
                        : {}
                }
            );

            setMessages((oldMessages) => [
                ...oldMessages,
                {
                    type: "ai",
                    text:
                        response.data.response ||
                        "I could not generate a response."
                }
            ]);
        } catch (error) {
            console.error("AI Support Error:", error);

            let errorText =
                "Unable to connect to AI Support.";

            if (error.response?.data?.detail) {
                errorText = error.response.data.detail;
            }

            setMessages((oldMessages) => [
                ...oldMessages,
                {
                    type: "ai",
                    text: errorText
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="ai-support-widget">

            {/* Floating Button */}
            {!isOpen && (
                <button
                    className="ai-support-button"
                    onClick={() => setIsOpen(true)}
                    title="AI Support"
                >
                    🤖
                </button>
            )}

            {/* Chat Box */}
            {isOpen && (
                <div className="ai-support-chat">

                    {/* Header */}
                    <div className="ai-support-header">

                        <div className="ai-support-title">

                            <span className="ai-support-title-icon">
                                🤖
                            </span>

                            <div>
                                <strong>AI Support</strong>

                                <span className="ai-support-online">
                                    ● Online
                                </span>
                            </div>

                        </div>

                        <button
                            className="ai-support-close"
                            onClick={() => setIsOpen(false)}
                        >
                            ×
                        </button>

                    </div>

                    {/* Messages */}
                    <div
                        className="ai-support-messages"
                        ref={messagesRef}
                    >

                        {messages.map((item, index) => (
                            <div
                                key={index}
                                className={
                                    item.type === "user"
                                        ? "ai-message ai-message-user"
                                        : "ai-message ai-message-ai"
                                }
                            >
                                {item.text}
                            </div>
                        ))}

                        {loading && (
                            <div className="ai-message ai-message-ai">
                                Thinking...
                            </div>
                        )}

                    </div>

                    {/* Quick Questions */}
                    <div className="ai-quick-questions">

                        <button
                            onClick={() =>
                                sendMessage(
                                    "How do I create a post?"
                                )
                            }
                        >
                            How do I create a post?
                        </button>

                        <button
                            onClick={() =>
                                sendMessage(
                                    "How do subscriptions work?"
                                )
                            }
                        >
                            How do subscriptions work?
                        </button>

                        <button
                            onClick={() =>
                                sendMessage(
                                    "I need billing help"
                                )
                            }
                        >
                            Billing help
                        </button>

                        <button
                            onClick={() =>
                                sendMessage(
                                    "Explain dashboard analytics"
                                )
                            }
                        >
                            Dashboard analytics
                        </button>

                    </div>

                    {/* Input */}
                    <div className="ai-support-input">

                        <input
                            type="text"
                            value={message}
                            placeholder="Ask something..."
                            onChange={(event) =>
                                setMessage(event.target.value)
                            }
                            onKeyDown={handleKeyDown}
                            disabled={loading}
                        />

                        <button
                            onClick={() => sendMessage()}
                            disabled={
                                loading ||
                                !message.trim()
                            }
                        >
                            ➤
                        </button>

                    </div>

                </div>
            )}

        </div>
    );
}

export default AISupport;
