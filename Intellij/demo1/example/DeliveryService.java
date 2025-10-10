/*package org.example; // 或你目前的 package

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import java.util.Objects;

public class DeliveryService {
    private static final Logger logger = LogManager.getLogger(DeliveryService.class);

    public void pickupOrder(Order order) {
        // 參數檢查應該放最前面，避免後續直接 NPE
        if (order == null) {
            logger.error("pickupOrder called with null order");
            // 可用自訂 Unchecked Exception，讓呼叫端選擇是否捕捉
            throw new InvalidOrderRuntimeException("Order is null");
        }

        logger.info("DeliveryService try pickup order {}", order.getId());

        if (order.getStatus() != OrderStatus.READY_FOR_PICKUP && order.getStatus() != OrderStatus.ACCEPTED) {
            logger.warn("Order {} is not ready for pickup (status={})", order.getId(), order.getStatus());
            return;
        }

        order.setStatus(OrderStatus.PICKED_UP);
        logger.info("Order {} picked up by delivery.", order.getId());
    }

    public void deliverOrder(Order order) {
        if (order == null) {
            logger.error("deliverOrder called with null order");
            throw new InvalidOrderRuntimeException("Order is null");
        }
        logger.info("Delivering order {}", order.getId());
        order.setStatus(OrderStatus.DELIVERED);
        logger.info("Order {} delivered to {}", order.getId(), order.getCustomerName());
    }
}
*/

/*
package org.example;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class DeliveryService {
    private static final Logger logger = LogManager.getLogger(DeliveryService.class);
    private final OrderService orderService;

    public DeliveryService(OrderService orderService) {
        this.orderService = orderService;
    }

    public void pickupOrder(Order order) {
        if (order == null) {
            logger.error("pickupOrder called with null order");
            throw new InvalidOrderRuntimeException("Order is null");
        }

        logger.info("DeliveryService try pickup order {}", order.getId());

        // 僅允許在 READY_FOR_PICKUP 或（容錯）ACCEPTED 時取餐
        switch (order.getStatus()) {
            case READY_FOR_PICKUP:
            case ACCEPTED:
                try {
                    orderService.transition(order, OrderStatus.PICKED_UP);
                    logger.info("Order {} picked up by delivery.", order.getId());
                } catch (OrderProcessingException e) {
                    // 應該不會發生，若真的違規就記 error 並上報
                    logger.error("Failed to transition to PICKED_UP: {}", e.getMessage(), e);
                    throw new InvalidOrderRuntimeException("Illegal pickup state: " + order.getStatus(), e);
                }
                break;
            default:
                logger.warn("Order {} is not ready for pickup (status={})", order.getId(), order.getStatus());
        }
    }

    public void deliverOrder(Order order) {
        if (order == null) {
            logger.error("deliverOrder called with null order");
            throw new InvalidOrderRuntimeException("Order is null");
        }
        logger.info("Delivering order {}", order.getId());
        try {
            orderService.transition(order, OrderStatus.DELIVERED);
            logger.info("Order {} delivered to {}", order.getId(), order.getCustomerName());
        } catch (OrderProcessingException e) {
            logger.error("Failed to transition to DELIVERED: {}", e.getMessage(), e);
            throw new InvalidOrderRuntimeException("Illegal deliver state: " + order.getStatus(), e);
        }
    }
}
*/


// DeliveryService：委派給 OrderService（取代原檔）
public class DeliveryService {
    private static final Logger logger = LogManager.getLogger(DeliveryService.class);
    private final OrderService orderService;

    public DeliveryService(OrderService orderService) { this.orderService = orderService; }

    public void pickupOrder(Order order) {
        if (order == null) { logger.error("pickupOrder called with null order"); throw new InvalidOrderRuntimeException("Order is null"); }
        logger.info("DeliveryService try pickup order {}", order.getId());
        switch (order.getStatus()) {
            case READY_FOR_PICKUP:
            case ACCEPTED:
                try {
                    orderService.transition(order, OrderStatus.PICKED_UP);
                    logger.info("Order {} picked up by delivery.", order.getId());
                } catch (OrderProcessingException e) {
                    logger.error("Failed to transition to PICKED_UP: {}", e.getMessage(), e);
                    throw new InvalidOrderRuntimeException("Illegal pickup state: " + order.getStatus(), e);
                }
                break;
            default:
                logger.warn("Order {} is not ready for pickup (status={})", order.getId(), order.getStatus());
        }
    }

    public void deliverOrder(Order order) {
        if (order == null) { logger.error("deliverOrder called with null order"); throw new InvalidOrderRuntimeException("Order is null"); }
        logger.info("Delivering order {}", order.getId());
        try {
            orderService.transition(order, OrderStatus.DELIVERED);
            logger.info("Order {} delivered to {}", order.getId(), order.getCustomerName());
        } catch (OrderProcessingException e) {
            logger.error("Failed to transition to DELIVERED: {}", e.getMessage(), e);
            throw new InvalidOrderRuntimeException("Illegal deliver state: " + order.getStatus(), e);
        }
    }
}
