package com.example.delivery;

import java.time.LocalDateTime;
import java.util.UUID;

public class Order {
    private final String id;
    private final String customerName;
    private final String restaurantName;
    private OrderStatus status;
    private final LocalDateTime createdAt;

    public Order(String customerName, String restaurantName) {
        this.id = UUID.randomUUID().toString();
        this.customerName = customerName;
        this.restaurantName = restaurantName;
        this.status = OrderStatus.PENDING;
        this.createdAt = LocalDateTime.now();
    }

    // getters / setters
    public String getId() { return id; }
    public String getCustomerName() { return customerName; }
    public String getRestaurantName() { return restaurantName; }
    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus status) { this.status = status; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    @Override
    public String toString() {
        return "Order{" +
                "id='" + id + '\'' +
                ", customerName='" + customerName + '\'' +
                ", restaurantName='" + restaurantName + '\'' +
                ", status=" + status +
                ", createdAt=" + createdAt +
                '}';
    }
}
