package com.example.delivery;

public enum OrderStatus {
    PENDING,         // 顧客已下單，等待餐廳接單
    ACCEPTED,        // 餐廳已接單
    PREPARING,       // 餐點製作中
    READY_FOR_PICKUP,// 餐點完成，等待外送員取餐
    PICKED_UP,       // 外送員已取餐
    DELIVERED,       // 已送達
    CANCELLED        // 訂單取消
}
