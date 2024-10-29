import { useQuery, useMutation, useQueryClient } from "react-query";
import { recordingQueries } from "../services/queries";

export const useRecordings = (routeId: string) => {
  return useQuery({
    queryKey: ['recordings', routeId],
    queryFn: () => recordingQueries.getRecordings(routeId),
    enabled: !!routeId
  });
};

export const useCreateRecording = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: recordingQueries.createRecording,
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ 
        queryKey: ['recordings']
      });
    }
  });
};

export const useRecordingsAnalysis = (recordingIds: string[]) => {
  return useQuery({
    queryKey: ['recordings', 'analysis', recordingIds],
    queryFn: () => recordingQueries.getAnalysis(recordingIds),
    enabled: recordingIds.length > 0
  });
};