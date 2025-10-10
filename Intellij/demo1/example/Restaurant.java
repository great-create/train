package com.example.delivery;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Restaurant {
    private static final Logger logger = LogManager.getLogger(Restaurant.class);
    private final String name;
    private boolean open;

    public Restaurant(String name, boolean open) {
        this.name = name;
        this.open = open;
    }

    public String getName() { return name; }
    public boolean isOpen() { return open; }
    public void setOpen(boolean open) { this.open = open; }

    /**
     * Accept order: 可能因為餐廳關閉、訂單資料錯誤而拋出 OrderProcessingException (checked)
     */
    public void acceptOrder(Order order) throws OrderProcessingException {
        logger.info("Restaurant {} received accept request for order {}", name, order.getId());

        // 業務檢核：餐廳關閉 → Checked Exception (業務錯誤，需呼叫端處理)
        if (!open) {
            logger.warn("Restaurant {} is closed — cannot accept order {}", name, order.getId());
            throw new OrderProcessingException("Restaurant " + name + " is closed");
        }

        // 參數檢查：若 order 為 null，這通常是程式邏輯錯誤 → 使用 Unchecked 或 IllegalArgumentException
        if (order == null) {
            logger.error("Received null order in acceptOrder for restaurant {}", name);
            throw new InvalidOrderRuntimeException("Order is null");
        }

        // 模擬某些非法狀況（例如: restaurant name mismatch）
        if (!order.getRestaurantName().equals(name)) {
            logger.warn("Order {} restaurant name mismatch: expected={}, actual={}",
                    order.getId(), name, order.getRestaurantName());
            // 視情況我們選擇拋出 checked，代表業務檢核失敗
            throw new OrderProcessingException("Order restaurant mismatch");
        }

        // 一切正常
        order.setStatus(OrderStatus.ACCEPTED);
        logger.info("Restaurant {} accepted order {} (status -> {})", name, order.getId(), order.getStatus());
    }
}
