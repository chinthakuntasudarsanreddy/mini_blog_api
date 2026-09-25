import { useAuth0 } from "@auth0/auth0-react";
import "./Login.css";

function Login() {
    const {
        loginWithRedirect,
        isLoading,
    } = useAuth0();

    const loginWithGoogle = () => {
        loginWithRedirect({
            authorizationParams: {
                connection: "google-oauth2",
            },
        });
    };

    const loginWithFacebook = () => {
        loginWithRedirect({
            authorizationParams: {
                connection: "facebook",
            },
        });
    };

    const loginWithEmail = () => {
        loginWithRedirect({
            authorizationParams: {
                screen_hint: "login",
            },
        });
    };

    const signup = () => {
        loginWithRedirect({
            authorizationParams: {
                screen_hint: "signup",
            },
        });
    };

    if (isLoading) {
        return (
            <div className="auth-loading">
                Loading...
            </div>
        );
    }

    return (
        <div className="auth-page">
            <div className="auth-card">

                <h1>Mini Blog</h1>

                <p className="auth-subtitle">
                    Sign in to continue
                </p>

                <button
                    className="social-button google-button"
                    onClick={loginWithGoogle}
                >
                    Continue with Google
                </button>

                <button
                    className="social-button facebook-button"
                    onClick={loginWithFacebook}
                >
                    Continue with Facebook
                </button>

                <div className="divider">
                    <span>OR</span>
                </div>

                <button
                    className="email-button"
                    onClick={loginWithEmail}
                >
                    Continue with Email
                </button>

                <p className="signup-text">
                    Don't have an account?
                    <button
                        className="signup-link"
                        onClick={signup}
                    >
                        Sign up
                    </button>
                </p>

            </div>
        </div>
    );
}

export default Login;