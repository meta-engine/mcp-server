package com.metaengine.demo.catalog.services;

import com.metaengine.demo.catalog.aggregates.Product;
import java.util.List;
import java.util.Optional;

/** ProductRepository persistence service for the catalog domain. */
public class ProductRepository {
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    public Optional<Product> findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
