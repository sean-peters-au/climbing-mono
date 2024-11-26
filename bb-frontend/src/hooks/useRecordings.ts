import { useQuery, useMutation, useQueryClient } from "react-query";
import { recordingQueries } from "../services/betaboard-backend/queries";

export const useRecordings = (routeId: string) => {
  return useQuery({
    queryKey: ['recordings', routeId],
    queryFn: () => recordingQueries.getRecordings(routeId),
    enabled: !!routeId
  });
};

export const useStartRecording = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: recordingQueries.startRecording,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ 
        queryKey: ['recordings']
      });
    }
  });
};

export const useStopRecording = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: recordingQueries.stopRecording,
    onSuccess: (data) => {
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