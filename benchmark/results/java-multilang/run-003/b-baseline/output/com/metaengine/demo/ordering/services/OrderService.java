package com.metaengine.demo.ordering.services;

import com.metaengine.demo.ordering.aggregates.Order;
import java.util.List;

/** OrderService domain service for the ordering domain. */
public class OrderService {
    /** Create a new Order from a partial input. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Order by its identifier. May return null. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Orders up to the given limit. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Order by its identifier. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
