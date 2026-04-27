import { Shipment } from '../aggregates/Shipment';

/** ShipmentService service. */
export class ShipmentService {
  create(input: Partial<Shipment>): Shipment { throw new Error('not implemented'); }
  findById(id: string): Shipment | null { throw new Error('not implemented'); }
  list(limit: number): Shipment[] { throw new Error('not implemented'); }
  delete(id: string): void { throw new Error('not implemented'); }
}
