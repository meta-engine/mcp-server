package com.metaengine.demo.shipping.services;

import com.metaengine.demo.shipping.aggregates.Shipment;
import java.util.List;

/** Gateway service that brokers shipments through external carriers. */
public class CarrierGateway {
    /** Submit a new shipment from the provided partial input. */
    public Shipment create(Shipment input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Look up a brokered shipment by id. Returns null when not found. */
    public Shipment findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} brokered shipments. */
    public List<Shipment> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Cancel a brokered shipment by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
