package com.example.delivery;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class App {
    private static final Logger logger = LogManager.getLogger(App.class);

    public static void main(String[] args) {
        // 建立模擬資料
        Restaurant restaurantOpen = new Restaurant("PastaHouse", true);
        Restaurant restaurantClosed = new Restaurant("SushiTime", false);

        Order goodOrder = new Order("Alice", "PastaHouse");
        Order mismatchOrder = new Order("Bob", "OtherRestaurant");
        Order orderForClosed = new Order("Cathy", "SushiTime");

        DeliveryService deliveryService = new DeliveryService();

        // 1) 正常流程
        try {
            logger.info("---- Start normal flow ----");
            restaurantOpen.acceptOrder(goodOrder);  // 可能拋 OrderProcessingException
            // 模擬餐點製作完成
            goodOrder.setStatus(OrderStatus.READY_FOR_PICKUP);
            deliveryService.pickupOrder(goodOrder);
            deliveryService.deliverOrder(goodOrder);
            logger.info("Finished normal flow for order {}", goodOrder.getId());
        } catch (OrderProcessingException e) {
            // Checked Exception 必須處理：記錄並決定回復策略
            logger.error("Business error when processing order: {}", e.getMessage(), e);
        } catch (RuntimeException e) {
            // Unchecked Exception（coding bug/環境問題）也要被捕捉並記錄
            logger.error("Unexpected runtime error: {}", e.getMessage(), e);
        }

        // 2) 餐廳關閉 → 會拋出 Checked Exception
        try {
            logger.info("---- Start closed-restaurant flow ----");
            restaurantClosed.acceptOrder(orderForClosed);
        } catch (OrderProcessingException e) {
            logger.warn("Order cannot be accepted because restaurant closed: {}", e.getMessage());
        }

        // 3) 訂單餐廳名稱不符合 → Checked Exception
        try {
            logger.info("---- Start mismatch flow ----");
            restaurantOpen.acceptOrder(mismatchOrder);
        } catch (OrderProcessingException e) {
            logger.warn("Order rejected due to mismatch: {}", e.getMessage());
        }

        // 4) 示範 Unchecked Exception: 呼叫 pickupOrder(null) 會拋出 InvalidOrderRuntimeException
        try {
            logger.info("---- Start runtime error (null) flow ----");
            deliveryService.pickupOrder(null); // 會丟出 Unchecked
        } catch (OrderProcessingException e) {
            // 不會來到這裡 (pickupOrder 不會丟 checked)，但為了示範捕捉型別混合
            logger.error("checked handler: {}", e.getMessage());
        } catch (RuntimeException e) {
            logger.error("Caught runtime exception: {}", e.getMessage(), e);
        }
    }
}
