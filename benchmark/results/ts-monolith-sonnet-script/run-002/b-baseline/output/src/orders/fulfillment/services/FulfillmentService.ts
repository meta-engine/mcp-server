import { Id } from '../../../shared/value-objects/Id';
import { Shipment } from '../aggregates/Shipment';

/** Service for managing shipment fulfillment records. */
export class FulfillmentService {
  create(input: Partial<Shipment>): Shipment {
    void input;
    throw new Error('not implemented');
  }

  findById(id: Id): Shipment | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): Shipment[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: Id): void {
    void id;
    throw new Error('not implemented');
  }
}
