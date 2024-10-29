import { useQuery } from "react-query";
import { wallQueries } from "../services/queries";

export const useWall = (id: string | undefined) => {
  return useQuery({
    queryKey: ['walls', id],
    queryFn: () => wallQueries.getWall(id!),
    enabled: !!id
  });
};