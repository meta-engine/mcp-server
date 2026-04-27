package com.metaengine.demo.ordering.services;

import com.metaengine.demo.ordering.aggregates.Order;
import java.util.List;

/** Application service exposing order operations. */
public class OrderService {
    /** Create an order from the provided partial input. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an order by id. Returns null when not found. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} orders. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an order by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
