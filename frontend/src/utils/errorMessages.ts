export type ErrorType =
  | "network_error"
  | "server_error"
  | "validation_error"
  | "unknown_error";

export function errorMessageFor(type: ErrorType) {
  switch (type) {
    case "network_error":
      return {
        title: "Network error",
        message: "We couldn't reach the server. Check your internet connection and try again.",
      };

    case "server_error":
      return {
        title: "Server error",
        message: "Something went wrong on our side — please try again in a moment.",
      };

    case "validation_error":
      return {
        title: "Invalid request",
        message: "Some preferences look invalid. Please review and try again.",
      };

    default:
      return {
        title: "Unexpected error",
        message: "An unexpected error occurred. Please try again.",
      };
  }
}
