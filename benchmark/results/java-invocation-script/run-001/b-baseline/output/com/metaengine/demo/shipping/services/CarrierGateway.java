package com.metaengine.demo.shipping.services;

import com.metaengine.demo.shipping.aggregates.Shipment;
import java.util.List;

/** CarrierGateway for the shipping domain. */
public class CarrierGateway {

    /** Hand off a Shipment to the carrier. */
    public Shipment create(Shipment input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Look up a Shipment by id; may return null. */
    public Shipment findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List shipments up to the given limit. */
    public List<Shipment> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a shipment by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
