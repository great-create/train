/*package com.example.delivery;

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
            deliveryService.pickupOrder(null); // 故意傳 null 以測試 Unchecked Exception 行為
        }  catch (RuntimeException e) {
            logger.error("Caught runtime exception: {}", e.getMessage(), e);
        }
    }
}
*/


package org.example;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.example.events.EventBus;
import org.example.events.listeners.DailyReportListener;
import org.example.events.listeners.LoggingListener;

public class App {
    private static final Logger logger = LogManager.getLogger(App.class);

    public static void main(String[] args) {
        ExceptionManager exceptionManager = new ExceptionManager();

        // 事件系統
        EventBus eventBus = new EventBus();
        LoggingListener loggingListener = new LoggingListener();
        DailyReportListener dailyReportListener = new DailyReportListener();
        eventBus.register(loggingListener);
        eventBus.register(dailyReportListener);

        // 每日報告（示範：每 15 秒輸出一次）
        DailyReportScheduler scheduler = new DailyReportScheduler(dailyReportListener, exceptionManager);
        scheduler.startAtFixedRate(5, 15); // 5 秒後開始、每 15 秒一份報告

        // 建構
        OrderService orderService = new OrderService(eventBus);
        DeliveryService deliveryService = new DeliveryService(orderService);
        Restaurant restaurant = new Restaurant("PastaHouse", true);

        // 正常流程（含延遲）
        Order order1 = new Order("Alice", "PastaHouse");
        try {
            logger.info("---- NORMAL FLOW ----");
            restaurant.acceptOrder(order1);
            orderService.transition(order1, OrderStatus.PREPARING);
            Delay.ms(1000, "Cooking"); // 模擬製作 1 秒
            orderService.transition(order1, OrderStatus.READY_FOR_PICKUP);

            deliveryService.pickupOrder(order1);
            Delay.ms(800, "Delivery"); // 模擬外送 0.8 秒
            deliveryService.deliverOrder(order1);
            //orderService.transition(order1, OrderStatus.DELIVERED);
        } catch (OrderProcessingException e) {
            logger.error("Business error: {}", e.getMessage(), e);
            exceptionManager.record(e);
        } catch (RuntimeException e) {
            logger.error("Runtime error: {}", e.getMessage(), e);
            exceptionManager.record(e);
        }

        // 取消案例
        Order order2 = new Order("Bob", "PastaHouse");
        try {
            logger.info("---- CANCEL FLOW ----");
            restaurant.acceptOrder(order2);
            orderService.transition(order2, OrderStatus.PREPARING);
            // 使用者臨時取消
            orderService.cancel(order2, "Customer changed mind");
        } catch (OrderProcessingException e) {
            logger.error("Business error: {}", e.getMessage(), e);
            exceptionManager.record(e);
        } catch (RuntimeException e) {
            logger.error("Runtime error: {}", e.getMessage(), e);
            exceptionManager.record(e);
        }

        // 範例：觸發一個 unchecked（看看統計）
        try {
            logger.info("---- RUNTIME ERROR EXAMPLE ----");
            deliveryService.pickupOrder(null); // 會拋 InvalidOrderRuntimeException（依你現有版本）
        } catch (RuntimeException e) {
            logger.error("Runtime error: {}", e.getMessage(), e);
            exceptionManager.record(e);
        }

        // 為了讓你看到至少一份「每日報告」，暫停幾秒（示範）
        Delay.ms(20000, "Wait for scheduled report"); // 20 秒

        scheduler.shutdown();
        logger.info("App finished.");
    }
}
