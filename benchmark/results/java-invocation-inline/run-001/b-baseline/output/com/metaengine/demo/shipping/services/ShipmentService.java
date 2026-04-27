package com.metaengine.demo.shipping.services;

import com.metaengine.demo.shipping.aggregates.Shipment;
import java.util.List;

/** Application service exposing shipment operations. */
public class ShipmentService {
    /** Create a shipment from the provided partial input. */
    public Shipment create(Shipment input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a shipment by id. Returns null when not found. */
    public Shipment findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} shipments. */
    public List<Shipment> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a shipment by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
