package com.example.delivery;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class DeliveryService {
    private static final Logger logger = LogManager.getLogger(DeliveryService.class);

    public void pickupOrder(Order order) {
        logger.info("DeliveryService try pickup order {}", order.getId());

        if (order == null) {
            logger.error("pickupOrder called with null order");
            throw new InvalidOrderRuntimeException("Order is null");
        }

        if (order.getStatus() != OrderStatus.READY_FOR_PICKUP && order.getStatus() != OrderStatus.ACCEPTED) {
            logger.warn("Order {} is not ready for pickup (status={})", order.getId(), order.getStatus());
            // 我們這裡選擇不拋 checked，僅記錄 warning，模擬外送員可能嘗試卻無法取餐
            return;
        }

        // 模擬取餐成功
        order.setStatus(OrderStatus.PICKED_UP);
        logger.info("Order {} picked up by delivery.", order.getId());
    }

    public void deliverOrder(Order order) {
        logger.info("Delivering order {}", order.getId());
        if (order == null) {
            logger.error("deliverOrder called with null order");
            throw new InvalidOrderRuntimeException("Order is null");
        }
        order.setStatus(OrderStatus.DELIVERED);
        logger.info("Order {} delivered to {}", order.getId(), order.getCustomerName());
    }
}
