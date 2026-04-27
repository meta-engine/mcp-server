package com.metaengine.demo.inventory.services;

import com.metaengine.demo.inventory.aggregates.StockItem;
import java.util.List;

/** StockRepository service for the inventory domain. */
public class StockRepository {

    /** Create a new StockItem. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a StockItem by id. May return null. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List stock items up to the given limit. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a StockItem by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
