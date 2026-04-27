package com.metaengine.demo.ordering.services;

import java.util.List;

import com.metaengine.demo.ordering.aggregates.Order;

/** OrderRepository persistence service. */
public class OrderRepository {

    /** Persist an Order from a partial input. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Order by id (may return null). */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List orders up to limit. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Order by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
