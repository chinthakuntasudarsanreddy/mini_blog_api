def generate_ai_response(message: str) -> str:
    """
    Generate a mock AI support response based on the user's question.
    This can later be replaced with a real AI API.
    """

    question = message.lower().strip()

    # -----------------------------
    # Posts
    # -----------------------------

    if any(keyword in question for keyword in [
        "create post",
        "create a post",
        "new post",
        "write a post",
        "add post",
    ]):
        return (
            "To create a post, open your Dashboard and select "
            "'Create Post'. Enter your title and content, upload an "
            "image if allowed by your subscription plan, and click "
            "'Publish'."
        )

    if any(keyword in question for keyword in [
        "edit post",
        "edit a post",
        "update post",
        "modify post",
    ]):
        return (
            "To edit a post, open your Dashboard and find the post "
            "you want to change. Select the Edit option, update the "
            "content, and save your changes."
        )

    if any(keyword in question for keyword in [
        "delete post",
        "delete a post",
        "remove post",
    ]):
        return (
            "To delete a post, open your Dashboard, find the post, "
            "select the Delete option, and confirm the deletion."
        )

    # -----------------------------
    # Subscriptions
    # -----------------------------

    if any(keyword in question for keyword in [
        "subscription",
        "subscription plan",
        "plans",
        "plan",
    ]):
        return (
            "The platform provides Basic, Premium, and Pro subscription "
            "plans. Each plan provides different limits for posts, images, "
            "likes, and comments. You can view your current subscription "
            "and available plans from the subscription section."
        )

    if any(keyword in question for keyword in [
        "basic plan",
        "basic subscription",
    ]):
        return (
            "The Basic plan is designed for users who need limited access. "
            "It allows 1 post and 1 image, with limited likes and comments."
        )

    if any(keyword in question for keyword in [
        "premium plan",
        "premium subscription",
    ]):
        return (
            "The Premium plan provides higher limits than Basic. "
            "It supports up to 2 posts and up to 2 images per post, "
            "with moderate interaction limits."
        )

    if any(keyword in question for keyword in [
        "pro plan",
        "pro subscription",
    ]):
        return (
            "The Pro plan provides unlimited access to posts and "
            "interactions according to the platform's available features."
        )

    if any(keyword in question for keyword in [
        "upgrade",
        "upgrade plan",
    ]):
        return (
            "To upgrade your subscription, open the Subscription section "
            "from your account or dashboard and select the plan you want "
            "to upgrade to."
        )

    # -----------------------------
    # Billing
    # -----------------------------

    if any(keyword in question for keyword in [
        "billing",
        "billing history",
        "invoice",
        "payment",
        "payments",
    ]):
        return (
            "You can view your billing information and previous billing "
            "records from the Billing section of your account. "
            "If you have a payment or invoice issue, please check the "
            "billing history for the transaction details."
        )

    # -----------------------------
    # Profile
    # -----------------------------

    if any(keyword in question for keyword in [
        "profile",
        "edit profile",
        "update profile",
        "change profile",
    ]):
        return (
            "To manage your profile, open your Profile or Account section. "
            "There you can update the information available for editing "
            "on your account."
        )

    if any(keyword in question for keyword in [
        "change password",
        "password",
    ]):
        return (
            "You can change your password from the account or security "
            "section if password management is enabled for your account."
        )

    # -----------------------------
    # Dashboard
    # -----------------------------

    if any(keyword in question for keyword in [
        "dashboard",
        "dashboard analytics",
        "analytics",
        "statistics",
        "stats",
    ]):
        return (
            "Dashboard analytics provide an overview of your platform "
            "activity. Depending on the available features, you may see "
            "information such as posts, likes, comments, and other "
            "engagement statistics."
        )

    # -----------------------------
    # Login / Account
    # -----------------------------

    if any(keyword in question for keyword in [
        "login",
        "log in",
        "sign in",
    ]):
        return (
            "To log in, open the Login page and enter your registered "
            "email and password. If you cannot log in, verify your "
            "credentials and try again."
        )

    if any(keyword in question for keyword in [
        "register",
        "registration",
        "sign up",
        "signup",
        "create account",
    ]):
        return (
            "To create an account, open the Registration or Sign Up page "
            "and provide the required information. After registration, "
            "you can log in and access your dashboard."
        )

    # -----------------------------
    # General FAQ
    # -----------------------------

    if any(keyword in question for keyword in [
        "help",
        "support",
        "what can you do",
        "what can i ask",
    ]):
        return (
            "I can help you with posts, subscriptions, billing, profile "
            "management, dashboard analytics, login, registration, and "
            "other general questions about the blog platform."
        )

    if any(keyword in question for keyword in [
        "hello",
        "hi",
        "hey",
    ]):
        return (
            "Hello! 👋 I'm your AI Support Assistant. "
            "You can ask me about creating posts, subscriptions, billing, "
            "your profile, dashboard analytics, or other platform features."
        )

    # -----------------------------
    # Default response
    # -----------------------------

    return (
        "I'm sorry, I don't have a specific answer for that yet. "
        "You can ask me about creating, editing, or deleting posts, "
        "subscriptions, billing, profile management, dashboard analytics, "
        "login, or general platform support."
    )