package com.metaengine.demo.ordering.services;

import java.util.List;

import com.metaengine.demo.ordering.aggregates.Order;

/** OrderService for the ordering domain. */
public class OrderService {

    /** Creates a new Order from the partial input. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Finds an Order by id. May return null. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Lists Orders up to the given limit. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Deletes the Order with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
