package com.metaengine.demo.inventory.services;

import java.util.List;

import com.metaengine.demo.inventory.aggregates.StockItem;

/** StockRepository persistence service. */
public class StockRepository {

    /** Persist a StockItem from a partial input. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a StockItem by id (may return null). */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List stock items up to limit. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a StockItem by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
