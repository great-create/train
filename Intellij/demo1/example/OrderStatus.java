/*package com.example.delivery;

public enum OrderStatus {
    PENDING,         // 顧客已下單，等待餐廳接單
    ACCEPTED,        // 餐廳已接單
    PREPARING,       // 餐點製作中
    READY_FOR_PICKUP,// 餐點完成，等待外送員取餐
    PICKED_UP,       // 外送員已取餐
    DELIVERED,       // 已送達
    CANCELLED        // 訂單取消
}
*/

package org.example;

import java.util.EnumSet;

public enum OrderStatus {
    PENDING,
    ACCEPTED,
    PREPARING,
    READY_FOR_PICKUP,
    PICKED_UP,
    DELIVERED,
    CANCELLED;

    // 合法轉移表（簡化版本）
    public boolean canTransitionTo(OrderStatus next) {
        switch (this) {
            case PENDING:          return EnumSet.of(ACCEPTED, CANCELLED).contains(next);
            case ACCEPTED:         return EnumSet.of(PREPARING, CANCELLED).contains(next);
            case PREPARING:        return EnumSet.of(READY_FOR_PICKUP, CANCELLED).contains(next);
            case READY_FOR_PICKUP: return EnumSet.of(PICKED_UP, CANCELLED).contains(next);
            case PICKED_UP:        return EnumSet.of(DELIVERED).contains(next);
            case DELIVERED:        return false;        // 終態
            case CANCELLED:        return false;        // 終態
            default:               return false;
        }
    }
}
