package com.example.delivery;

/**
 * Unchecked Exception，代表程式邏輯或環境錯誤
 */
public class InvalidOrderRuntimeException extends RuntimeException {
    public InvalidOrderRuntimeException(String message) {
        super(message);
    }

    public InvalidOrderRuntimeException(String message, Throwable cause) {
        super(message, cause);
    }
}
