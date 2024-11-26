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
      queryClient.invalidateQueries(['routes', wallId]);
    }
  });
};

export const useUpdateRoute = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({
      wallId,
      routeId,
      routeData,
    }: {
      wallId: string;
      routeId: string;
      routeData: CreateRouteBody;
    }) => routeQueries.updateRoute({ wallId, routeId, routeData }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries(['routes', variables.wallId]);
    },
  });
};