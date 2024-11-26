import { useQuery } from "react-query";
import { wallQueries } from "../services/betaboard-backend/queries";

export const useWalls = () => {
  return useQuery({
    queryKey: ['walls'],
    queryFn: wallQueries.getWalls
  });
};