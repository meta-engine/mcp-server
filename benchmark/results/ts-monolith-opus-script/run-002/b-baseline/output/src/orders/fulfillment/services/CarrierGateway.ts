import { Shipment } from "../aggregates/Shipment";
import { Id } from "../../../shared/value-objects/Id";

/** External-carrier integration boundary for shipments. */
export class CarrierGateway {
  create(input: Partial<Shipment>): Shipment {
    void input;
    throw new Error("not implemented");
  }

  findById(id: Id): Shipment | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): Shipment[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: Id): void {
    void id;
    throw new Error("not implemented");
  }
}
