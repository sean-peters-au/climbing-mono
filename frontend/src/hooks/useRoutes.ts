import { useQuery, useMutation, useQueryClient } from "react-query";
import { CreateRouteBody, routeQueries } from "../services/betaboard-backend/queries";

export const useRoutes = (wallId: string) => {
  return useQuery({
    queryKey: ['routes', wallId],
    queryFn: () => routeQueries.getRoutes(wallId),
    enabled: !!wallId
  });
};

export const useCreateRoute = (wallId: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (routeData: CreateRouteBody) => 
      routeQueries.createRoute({ wallId, routeData }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes', wallId] });
    }
  });
};