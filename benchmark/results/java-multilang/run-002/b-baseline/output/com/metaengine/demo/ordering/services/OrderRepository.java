package com.metaengine.demo.ordering.services;

import java.util.List;
import com.metaengine.demo.ordering.aggregates.Order;

/** OrderRepository in the ordering domain. */
public class OrderRepository {
    /** Create a new Order. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Order by id. Returns null if not found. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Orders up to limit. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Order by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
