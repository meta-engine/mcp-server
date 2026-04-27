import { Shipment } from '../aggregates/shipment';
import { Id } from '../../../shared/value-objects/id';

export class CarrierGateway {

  create(input: Partial<Shipment>): Shipment { throw new Error('not implemented'); }

  findById(id: Id): Shipment | null { throw new Error('not implemented'); }

  list(limit: number): Shipment[] { throw new Error('not implemented'); }

  delete(id: Id): void { throw new Error('not implemented'); }
}
