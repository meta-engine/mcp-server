import { Id } from '../../../shared/value-objects/Id';
import { Shipment } from '../aggregates/Shipment';

/** Gateway for integrating with external carrier APIs. */
export class CarrierGateway {
  create(input: Partial<Shipment>): Shipment { throw new Error('not implemented'); }
  findById(id: Id): Shipment | null { throw new Error('not implemented'); }
  list(limit: number): Shipment[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
