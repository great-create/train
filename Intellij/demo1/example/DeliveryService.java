package org.example; // 或你目前的 package

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
