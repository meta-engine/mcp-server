package com.metaengine.demo.ordering.services;

import com.metaengine.demo.ordering.aggregates.Order;
import java.util.List;

/** Persistence gateway for orders. */
public class OrderRepository {
    /** Persist a new order from the provided partial input. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load an order by id. Returns null when not found. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} orders. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove an order by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
