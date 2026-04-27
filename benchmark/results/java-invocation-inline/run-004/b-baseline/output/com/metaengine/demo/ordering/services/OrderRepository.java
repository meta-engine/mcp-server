package com.metaengine.demo.ordering.services;

import java.util.List;
import com.metaengine.demo.ordering.aggregates.Order;

/** OrderRepository persistence service. */
public class OrderRepository {
    /** Persist a new Order. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Order by id; returns null if not found. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to limit Orders. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Order by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
