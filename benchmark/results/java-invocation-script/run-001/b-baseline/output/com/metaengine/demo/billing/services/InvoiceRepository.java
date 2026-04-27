package com.metaengine.demo.billing.services;

import com.metaengine.demo.billing.aggregates.Invoice;
import java.util.List;

/** InvoiceRepository for the billing domain. */
public class InvoiceRepository {

    /** Persist a new Invoice. */
    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load an Invoice by id; may return null. */
    public Invoice findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List invoices up to the given limit. */
    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an invoice by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
