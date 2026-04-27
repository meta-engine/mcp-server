import { Shipment } from "../aggregates/Shipment.js";

/** ShipmentRepository domain service. */
export class ShipmentRepository {
  create(input: Partial<Shipment>): Shipment {
    void input;
    throw new Error("not implemented");
  }

  findById(id: string): Shipment | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): Shipment[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: string): void {
    void id;
    throw new Error("not implemented");
  }
}
