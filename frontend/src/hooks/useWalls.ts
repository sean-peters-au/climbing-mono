import { useQuery } from "react-query";
import { wallQueries } from "../services/queries";

export const useWalls = () => {
  return useQuery({
    queryKey: ['walls'],
    queryFn: wallQueries.getWalls
  });
};