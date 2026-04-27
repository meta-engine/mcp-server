package com.metaengine.demo.ordering.services;

import java.util.List;

import com.metaengine.demo.ordering.aggregates.Order;

/** OrderRepository for the ordering domain. */
public class OrderRepository {

    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
