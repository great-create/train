package com.example.delivery;

/**
 * Checked Exception，用於業務層面需要強制處理的錯誤
 */
public class OrderProcessingException extends Exception {
    public OrderProcessingException(String message) {
        super(message);
    }

    public OrderProcessingException(String message, Throwable cause) {
        super(message, cause);
    }
}
