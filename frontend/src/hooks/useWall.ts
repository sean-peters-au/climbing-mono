import { useQuery, useMutation, useQueryClient } from "react-query";
import { wallQueries } from "../services/queries";

export const useWall = (id: string | undefined) => {
  return useQuery({
    queryKey: ['walls', id],
    queryFn: () => wallQueries.getWall(id!),
    enabled: !!id
  });
};

export const useDeleteHold = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async ({ wallId, holdId }: { wallId: string; holdId: string }) => {
      await wallQueries.deleteHold(wallId, holdId);
    },
    {
      onSuccess: (_data, variables) => {
        const { wallId } = variables;
        queryClient.invalidateQueries(['walls', wallId]);
      },
    }
  );
};

export const useAddHold = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async ({
      wallId,
      bbox,
      mask,
    }: {
      wallId: string;
      bbox: number[];
      mask: boolean[][];
    }) => {
      await wallQueries.addHold(wallId, { bbox, mask });
    },
    {
      onSuccess: (_data, variables) => {
        const { wallId } = variables;
        queryClient.invalidateQueries(['walls', wallId]);
      },
    }
  );
};
