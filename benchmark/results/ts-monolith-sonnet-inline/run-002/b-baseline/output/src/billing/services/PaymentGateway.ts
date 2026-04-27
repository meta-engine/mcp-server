import { Id } from '../../shared/value-objects/Id';
import { Invoice } from '../aggregates/Invoice';

/** Gateway for processing payments against invoices. */
export class PaymentGateway {
  create(input: Partial<Invoice>): Invoice {
    void input;
    throw new Error('not implemented');
  }

  findById(id: Id): Invoice | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): Invoice[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: Id): void {
    void id;
    throw new Error('not implemented');
  }
}
