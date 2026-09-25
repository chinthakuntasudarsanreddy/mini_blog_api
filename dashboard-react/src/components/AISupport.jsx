import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "../ai-support.css";


const API_URL =
    import.meta.env.VITE_API_URL ||
    "http://127.0.0.1:8000";


function AISupport() {

    const [isOpen, setIsOpen] = useState(false);

    const [message, setMessage] = useState("");

    const [messages, setMessages] = useState([]);

    const [loading, setLoading] = useState(false);

    const chatBodyRef = useRef(null);


    // ========================================================
    // GET AUTH0 ACCESS TOKEN
    // ========================================================

    const getAccessToken = () => {

        const token =
            localStorage.getItem(
                "access_token"
            );

        return token;
    };


    // ========================================================
    // LOAD CHAT HISTORY
    // ========================================================

    useEffect(() => {

        if (isOpen) {

            loadChatHistory();

        }

    }, [isOpen]);


    // ========================================================
    // AUTO SCROLL
    // ========================================================

    useEffect(() => {

        if (chatBodyRef.current) {

            chatBodyRef.current.scrollTop =
                chatBodyRef.current.scrollHeight;

        }

    }, [messages, loading]);


    // ========================================================
    // LOAD HISTORY
    // ========================================================

    const loadChatHistory = async () => {

        try {

            const token =
                getAccessToken();


            if (!token) {

                console.warn(
                    "Auth0 access token not found."
                );

                return;
            }


            const response =
                await axios.get(
                    `${API_URL}/api/ai-support/history`,
                    {
                        headers: {
                            Authorization:
                                `Bearer ${token}`,
                        },
                    }
                );


            const history = [];


            if (Array.isArray(response.data)) {

                response.data.forEach(
                    (chat) => {

                        history.push({
                            id:
                                `${chat.id}-question`,
                            type: "user",
                            text:
                                chat.question,
                        });


                        history.push({
                            id:
                                `${chat.id}-answer`,
                            type: "ai",
                            text:
                                chat.ai_response,
                        });

                    }
                );

            }


            setMessages(history);


        } catch (error) {

            console.error(
                "Could not load AI support history:",
                error
            );


            if (
                error.response?.status === 401
            ) {

                console.error(
                    "Auth0 token was rejected by AI Support history API."
                );

            }

        }

    };


    // ========================================================
    // SEND MESSAGE
    // ========================================================

    const sendMessage = async () => {

        const trimmedMessage =
            message.trim();


        if (
            !trimmedMessage ||
            loading
        ) {

            return;

        }


        const token =
            getAccessToken();


        // ----------------------------------------------------
        // Require authentication
        // ----------------------------------------------------

        if (!token) {

            const errorMessage = {

                id:
                    `error-${Date.now()}`,

                type: "ai",

                text:
                    "Please log in before using AI Support.",
            };


            setMessages(
                (previous) => [
                    ...previous,
                    errorMessage,
                ]
            );


            return;
        }


        // ----------------------------------------------------
        // Add user's message
        // ----------------------------------------------------

        const userMessage = {

            id:
                `user-${Date.now()}`,

            type: "user",

            text:
                trimmedMessage,
        };


        setMessages(
            (previous) => [
                ...previous,
                userMessage,
            ]
        );


        setMessage("");

        setLoading(true);


        try {

            // ------------------------------------------------
            // Send request to FastAPI
            // ------------------------------------------------

            const response =
                await axios.post(

                    `${API_URL}/api/ai-support/`,

                    {
                        message:
                            trimmedMessage,
                    },

                    {
                        headers: {
                            "Content-Type":
                                "application/json",

                            Authorization:
                                `Bearer ${token}`,
                        },
                    }

                );


            // ------------------------------------------------
            // AI response
            // ------------------------------------------------

            const aiMessage = {

                id:
                    `ai-${Date.now()}`,

                type: "ai",

                text:
                    response.data?.ai_response ||
                    response.data?.response ||
                    "I could not generate a response.",
            };


            setMessages(
                (previous) => [
                    ...previous,
                    aiMessage,
                ]
            );


        } catch (error) {

            console.error(
                "AI Support request failed:",
                error
            );


            let errorText =
                "Sorry, something went wrong. Please try again.";


            // ------------------------------------------------
            // Authentication error
            // ------------------------------------------------

            if (
                error.response?.status === 401
            ) {

                errorText =
                    "Your login session is not authorized for AI Support. Please log out and log in again.";

            }


            // ------------------------------------------------
            // User not found
            // ------------------------------------------------

            else if (
                error.response?.status === 404
            ) {

                errorText =
                    "Your account was not found in the blog database. Please log in again.";

            }


            // ------------------------------------------------
            // Server error
            // ------------------------------------------------

            else if (
                error.response?.status >= 500
            ) {

                errorText =
                    "The AI Support server encountered an error. Please try again.";

            }


            const errorMessage = {

                id:
                    `error-${Date.now()}`,

                type: "ai",

                text:
                    errorText,
            };


            setMessages(
                (previous) => [
                    ...previous,
                    errorMessage,
                ]
            );


        } finally {

            setLoading(false);

        }

    };


    // ========================================================
    // ENTER KEY
    // ========================================================

    const handleKeyDown = (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    };


    // ========================================================
    // QUICK SUGGESTION
    // ========================================================

    const askSuggestion = (question) => {

        setMessage(question);

    };


    // ========================================================
    // UI
    // ========================================================

    return (

        <div className="app">


            {/* ==================================================
                CHAT WINDOW
            ================================================== */}

            {isOpen && (

                <div className="support-chat">


                    {/* HEADER */}

                    <div className="chat-header">

                        <div className="chat-title">

                            <div className="bot-avatar">
                                🤖
                            </div>


                            <div>

                                <h2>
                                    AI Support
                                </h2>

                                <span>
                                    ● Online
                                </span>

                            </div>

                        </div>


                        <button
                            className="close-button"
                            onClick={() =>
                                setIsOpen(false)
                            }
                            aria-label="Close AI Support"
                        >
                            ×
                        </button>

                    </div>


                    {/* CHAT BODY */}

                    <div
                        className="chat-body"
                        ref={chatBodyRef}
                    >


                        {/* EMPTY CHAT */}

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


                        {/* MESSAGES */}

                        {messages.map(
                            (item) => (

                                <div
                                    key={item.id}
                                    className={
                                        `message-row ${item.type}`
                                    }
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

                            )
                        )}


                        {/* TYPING */}

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


                    {/* INPUT */}

                    <div className="chat-input-area">

                        <textarea
                            value={message}
                            onChange={(event) =>
                                setMessage(
                                    event.target.value
                                )
                            }
                            onKeyDown={handleKeyDown}
                            placeholder="Ask something..."
                            rows="1"
                            disabled={loading}
                        />


                        <button
                            className="send-button"
                            onClick={sendMessage}
                            disabled={
                                !message.trim() ||
                                loading
                            }
                            aria-label="Send message"
                        >
                            ➤
                        </button>

                    </div>


                    {/* FOOTER */}

                    <div className="chat-footer">

                        AI Support Assistant

                    </div>

                </div>

            )}


            {/* ==================================================
                FLOATING BUTTON
            ================================================== */}

            <button
                className={
                    `support-button ${
                        isOpen ? "opened" : ""
                    }`
                }
                onClick={() =>
                    setIsOpen(
                        (previous) =>
                            !previous
                    )
                }
                aria-label="Open AI Support"
            >

                {isOpen ? "×" : "💬"}

            </button>


        </div>

    );

}


export default AISupport;