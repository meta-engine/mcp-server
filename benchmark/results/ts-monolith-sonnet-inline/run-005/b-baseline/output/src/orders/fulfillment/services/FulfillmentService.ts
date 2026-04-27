import { Id } from '../../../shared/value-objects/Id';
import { Shipment } from '../aggregates/Shipment';

/** Manages shipment fulfillment operations. */
export class FulfillmentService {
  create(input: Partial<Shipment>): Shipment { throw new Error('not implemented'); }
  findById(id: Id): Shipment | null { throw new Error('not implemented'); }
  list(limit: number): Shipment[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
